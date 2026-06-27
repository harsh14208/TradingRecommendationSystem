"""
services/cohort_edge_gate.py

Self-calibrating cohort expected-value gate (QENG-COHORT).

THE PROBLEM THIS REPLACES
-------------------------
The system has one real edge (long, multi-day-hold, mean-reversion on large-cap
tech). The same scoring machinery is applied to directions / styles / sectors
where that edge does not exist, diluting realized Sharpe toward zero. Because
entry alpha is exhausted (score/quality_score/meta-model are ~random at entry),
the confidence number cannot separate profitable cohorts from unprofitable ones.

Historically the unprofitable regions were suppressed with HARDCODED lists —
LONG_ONLY, BLOCKED_SECTORS, BLOCKED_TICKERS, per-style floors, the one-off
intraday safety rail. Each is a manual patch tuned to a recent window; it goes
stale on regime change and must be re-tuned by hand.

THE FIX
-------
One data-driven layer that learns, from the system's OWN realized outcomes,
which cohorts have positive net edge — and gates / sizes the rest accordingly.
It generalizes the existing ``_intraday_safety_blocked()`` rail to every
``(action, style, sector)`` cohort:

  1. Trailing-window realized outcomes are bucketed by cohort.
  2. Each cohort's mean NET edge (gross outcome − round-trip friction) is
     estimated with empirical-Bayes shrinkage toward its parent
     (cohort → action×style → global), so thin/new cohorts borrow strength
     instead of being blocked forever or trusted on noise.
  3. A cohort delivers only if its LOWER confidence bound on net edge > 0.
  4. Survivors are sized proportional to shrunk net edge.
  5. Recomputed nightly on a rolling window → cohorts auto-recover when they
     turn positive. No constant is ever hand-edited.

Cold-start safety: until enough resolved signals exist, the gate is a
passthrough (delivers everything at neutral size) so it can never starve a
fresh deployment.
"""

from __future__ import annotations

import json
import logging
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

log = logging.getLogger("signal.trade.cohort_edge")

# ── Tunables (these are the ONLY knobs; everything else is learned) ────────────
WINDOW_DAYS = 180  # trailing window of resolved signals used to estimate edge
FRICTION = 0.5  # round-trip cost (%) subtracted from gross outcome → net edge
N_MIN_OWN = 20  # below this, a cohort's own mean is heavily shrunk to its parent
SHRINK_K = 20.0  # empirical-Bayes pseudo-count: weight of the parent prior
Z = 1.0  # lower-bound = shrunk_net − Z·SE  (deliver iff > 0); ~1 SE above zero
GLOBAL_MIN_N = 50  # below this many total resolved signals → passthrough mode
TARGET_EDGE = 3.0  # net % that maps to the top of the sizing range
SIZE_CLAMP = (0.5, 1.5)  # cohort size multiplier range (one factor in the L-stack)

# Persisted snapshot (durable + observable; mirrors calibration.json convention)
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
COHORT_EDGE_PATH = os.path.join(_DATA_DIR, "cohort_edges.json")
_CACHE_TTL_SECONDS = 6 * 3600

# In-memory cache: {"generated_at": float_epoch, "snapshot": dict}
_CACHE: dict = {"loaded_at": 0.0, "snapshot": None}


@dataclass(frozen=True)
class CohortDecision:
    """Result of a cohort lookup. ``deliver`` gates; ``size_mult`` sizes."""

    deliver: bool
    size_mult: float
    reason: str
    n: int
    net_edge: float  # shrunk mean net edge (%)
    lb_net: float  # lower confidence bound on net edge (%)
    matched_key: str  # which hierarchy level actually answered (audit)


def _cohort_key(action: str, style: str, sector: str | None) -> str:
    return f"{action}|{style}|{sector or 'NONE'}"


def _parent_key(action: str, style: str) -> str:
    return f"{action}|{style}"


# ── Estimation ────────────────────────────────────────────────────────────────


def _mean_std(vals: list[float]) -> tuple[float, float]:
    n = len(vals)
    if n == 0:
        return 0.0, 0.0
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var)


def compute_snapshot(rows: list[tuple[str, str, str | None, float]]) -> dict:
    """Build the full cohort-edge snapshot from raw resolved rows.

    rows: list of (action, style, sector, gross_outcome_pct).

    Pure function (no DB / IO) so it is trivially unit-testable.
    """
    # Net outcome per row.
    recs = [(a, s or "swing", sec, float(o) - FRICTION) for (a, s, sec, o) in rows]
    total_n = len(recs)

    # Global prior.
    g_vals = [r[3] for r in recs]
    g_mean, g_std = _mean_std(g_vals)
    pooled_std = g_std if g_std > 0 else 1.0  # fallback dispersion for thin cohorts

    # Parent (action × style) and cohort (action × style × sector) buckets.
    parents: dict[str, list[float]] = {}
    cohorts: dict[str, list[float]] = {}
    cohort_meta: dict[str, tuple[str, str, str | None]] = {}
    for a, s, sec, net in recs:
        pk = _parent_key(a, s)
        ck = _cohort_key(a, s, sec)
        parents.setdefault(pk, []).append(net)
        cohorts.setdefault(ck, []).append(net)
        cohort_meta[ck] = (a, s, sec)

    passthrough = total_n < GLOBAL_MIN_N

    def _shrink(raw_mean: float, n: int, prior_mean: float) -> float:
        # Empirical-Bayes: blend cohort mean with prior by pseudo-count K.
        return (n * raw_mean + SHRINK_K * prior_mean) / (n + SHRINK_K)

    # Parent estimates shrink toward global.
    parent_est: dict[str, dict] = {}
    for pk, vals in parents.items():
        n = len(vals)
        raw_mean, _ = _mean_std(vals)
        shrunk = _shrink(raw_mean, n, g_mean)
        parent_est[pk] = {"n": n, "raw_net": round(raw_mean, 4), "net": round(shrunk, 4)}

    # Cohort estimates shrink toward their parent (which already shrank to global).
    cohort_est: dict[str, dict] = {}
    for ck, vals in cohorts.items():
        a, s, sec = cohort_meta[ck]
        pk = _parent_key(a, s)
        n = len(vals)
        raw_mean, raw_std = _mean_std(vals)
        prior = parent_est[pk]["net"]
        shrunk = _shrink(raw_mean, n, prior)
        # Effective sample size grows with the prior weight; dispersion falls back
        # to the pooled std when the cohort is too thin to estimate its own.
        n_eff = n + SHRINK_K
        sd = raw_std if (n >= N_MIN_OWN and raw_std > 0) else pooled_std
        se = sd / math.sqrt(n_eff)
        lb = shrunk - Z * se
        deliver = passthrough or lb > 0.0
        cohort_est[ck] = {
            "action": a,
            "style": s,
            "sector": sec,
            "n": n,
            "raw_net": round(raw_mean, 4),
            "net": round(shrunk, 4),
            "se": round(se, 4),
            "lb_net": round(lb, 4),
            "deliver": deliver,
            "size_mult": _size_mult(shrunk),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": WINDOW_DAYS,
        "friction": FRICTION,
        "total_n": total_n,
        "passthrough": passthrough,
        "global": {"n": total_n, "net": round(g_mean, 4), "std": round(g_std, 4)},
        "parents": parent_est,
        "cohorts": cohort_est,
    }


def _size_mult(net_edge: float) -> float:
    """Map a shrunk net edge (%) to a position-size multiplier in SIZE_CLAMP.

    net_edge = 0  → midpoint of clamp; +TARGET_EDGE → top; ≤−TARGET_EDGE → floor.
    """
    lo, hi = SIZE_CLAMP
    mid = (lo + hi) / 2.0
    raw = mid + (net_edge / TARGET_EDGE) * (hi - mid)
    return round(min(max(raw, lo), hi), 3)


# ── Persistence + cache ───────────────────────────────────────────────────────


def _persist(snapshot: dict) -> None:
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        tmp = COHORT_EDGE_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        os.replace(tmp, COHORT_EDGE_PATH)
    except Exception:
        log.warning("[cohort_edge] failed to persist snapshot", exc_info=True)  # pragma: no mutate


# Disk loading can be disabled (the test suite sets this so unit tests of other
# gates aren't coupled to a real on-disk snapshot — they get cold-start passthrough).
_DISK_LOAD_ENABLED = True


def set_disk_load_enabled(enabled: bool) -> None:
    global _DISK_LOAD_ENABLED
    _DISK_LOAD_ENABLED = enabled


def _load_from_disk() -> dict | None:
    if not _DISK_LOAD_ENABLED:
        return None
    try:
        with open(COHORT_EDGE_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        log.warning("[cohort_edge] failed to load snapshot", exc_info=True)  # pragma: no mutate
        return None


def _get_snapshot() -> dict | None:
    """Return the cached snapshot, loading from disk if the cache is cold/stale."""
    now = time.time()
    if _CACHE["snapshot"] is not None and (now - _CACHE["loaded_at"]) < _CACHE_TTL_SECONDS:
        return _CACHE["snapshot"]
    snap = _load_from_disk()
    _CACHE["snapshot"] = snap
    _CACHE["loaded_at"] = now
    return snap


def cache_snapshot(snapshot: dict | None) -> None:
    """Install a snapshot into the in-memory cache (used after a refresh / in tests)."""
    _CACHE["snapshot"] = snapshot
    _CACHE["loaded_at"] = time.time()


async def refresh_cohort_edges(db) -> dict:
    """Recompute cohort edges from the DB, persist + cache, return the snapshot.

    Safe to call from a background job or on startup. On any failure it logs and
    returns the last snapshot (or a passthrough stub) so callers never break.
    """
    try:
        from models import Signal

        cutoff = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
        result = await db.execute(
            select(Signal.action, Signal.style, Signal.sector_etf, Signal.outcome_pct).where(
                Signal.outcome_pct.isnot(None),
                Signal.created_at >= cutoff,
                Signal.action.in_(("BUY", "SELL")),
            )
        )
        rows = [(r[0], r[1], r[2], r[3]) for r in result.all()]
        snap = compute_snapshot(rows)
        _persist(snap)
        cache_snapshot(snap)
        n_block = sum(1 for c in snap["cohorts"].values() if not c["deliver"])
        log.info(
            "[cohort_edge] refreshed: total_n=%d passthrough=%s cohorts=%d blocked=%d",
            snap["total_n"],
            snap["passthrough"],
            len(snap["cohorts"]),
            n_block,
        )
        return snap
    except Exception:
        log.warning("[cohort_edge] refresh failed; keeping previous snapshot", exc_info=True)  # pragma: no mutate
        return _get_snapshot() or {}


# ── Decision lookup (the hot path called per signal) ──────────────────────────


def get_cohort_decision(action: str, style: str, sector: str | None) -> CohortDecision:
    """Return the gate + sizing decision for a signal's cohort.

    Hierarchical fallback at query time: exact cohort (if it has enough samples)
    → parent (action×style) → global. Cold start / unknown → passthrough (deliver,
    neutral size) so the gate never blocks on absent data.
    """
    snap = _get_snapshot()
    if not snap:
        return CohortDecision(True, 1.0, "cohort gate cold-start (no snapshot)", 0, 0.0, 0.0, "none")
    if snap.get("passthrough"):
        return CohortDecision(
            True,
            1.0,
            f"cohort gate passthrough (n={snap.get('total_n', 0)}<{GLOBAL_MIN_N})",
            0,
            0.0,
            0.0,
            "passthrough",
        )

    style = style or "swing"
    ck = _cohort_key(action, style, sector)
    cohorts = snap.get("cohorts", {})
    c = cohorts.get(ck)
    if c is not None and c["n"] >= N_MIN_OWN:
        reason = _decision_reason(c["deliver"], "cohort", ck, c)
        return CohortDecision(c["deliver"], c["size_mult"], reason, c["n"], c["net"], c["lb_net"], ck)

    # Thin/absent cohort → fall back to the parent (action × style).
    pk = _parent_key(action, style)
    p = snap.get("parents", {}).get(pk)
    if p is not None:
        # Parent has no precomputed lb/size; derive from its shrunk net.
        deliver = p["net"] > 0.0
        size = _size_mult(p["net"])
        # If the specific cohort exists but is thin, still honor a hard-negative
        # cohort signal when present (defense against a good parent masking a bad child).
        if c is not None and not c["deliver"] and c["n"] >= 5:
            return CohortDecision(
                False, c["size_mult"], _decision_reason(False, "cohort(thin)", ck, c), c["n"], c["net"], c["lb_net"], ck
            )
        reason = _decision_reason(deliver, "parent", pk, {"net": p["net"], "n": p["n"]})
        return CohortDecision(deliver, size, reason, p["n"], p["net"], p["net"], pk)

    # Unknown action/style entirely → defer to global, lean permissive.
    g = snap.get("global", {})
    g_net = g.get("net", 0.0)
    return CohortDecision(
        g_net >= 0.0,
        _size_mult(g_net),
        f"cohort gate global fallback (net={g_net:+.2f}%)",
        g.get("n", 0),
        g_net,
        g_net,
        "global",
    )


def _decision_reason(deliver: bool, level: str, key: str, est: dict) -> str:
    verb = "delivers" if deliver else "BLOCKED"
    return (
        f"cohort-EV {verb} [{level} {key}] "
        f"net={est.get('net', 0.0):+.2f}% lb={est.get('lb_net', est.get('net', 0.0)):+.2f}% n={est.get('n', 0)}"
    )


def snapshot_for_admin() -> dict:
    """Return the current snapshot (loading from disk if needed) for observability."""
    return _get_snapshot() or {}
