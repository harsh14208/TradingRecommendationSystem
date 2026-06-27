"""Point-in-time ticker performance gate.

Replaces the static defensive-ticker BUY blocklist with a decay-weighted,
forward-looking hit-rate gate.  A ticker is blocked only when its own recent
resolved signals show a poor win rate with sufficient sample size.  Auto-
retirement is built in: when forward performance improves, the gate unblocks
automatically.

Stage B wiring runs the gate in **shadow mode** alongside the legacy static
blocklist so the two can be compared before the static list is removed.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from .base import GateBase, SignalContext

log = logging.getLogger("signal.trade.engine")

# Lookback window for resolved signals.
_WINDOW_DAYS = 180
# Exponential-decay half-life for older outcomes (days).
_DECAY_HALFLIFE_DAYS = 30.0
# Minimum resolved-signal count to hard-block a ticker.
_MIN_N_BLOCK = 5
# Minimum count for a caution (size reduction) instead of a hard block.
_MIN_N_CAUTION = 3
# Block if decay-weighted win rate is below this threshold.
_BLOCK_THRESHOLD = 0.40
# Caution / size-reduction threshold.
_CAUTION_THRESHOLD = 0.50
# Floor ATR% rank below which we reduce size instead of blocking (low-energy
# drift is often a false positive for the performance gate).
_ATR_RANK_FLOOR = 20.0
# Size multiplier in caution regime.
_CAUTION_SIZE_MULT = 0.75

# In-memory cache refreshed from DB or tests.
_CACHE: dict = {"snapshot": None, "loaded_at": 0.0}


@dataclass(frozen=True)
class TickerPerformanceDecision:
    """Decision produced by the ticker-performance gate."""

    block: bool
    size_mult: float
    reason: str
    n: int
    win_rate: float  # decay-weighted
    raw_wr: float
    cohort_key: str
    validation_type: str


@dataclass
class TickerPerformanceSnapshot:
    """Read-only snapshot of ticker-specific performance."""

    tickers: dict[tuple[str, str], dict]
    total_n: int
    computed_at: datetime
    window_days: int

    def get(self, ticker: str, action: str) -> dict | None:
        return self.tickers.get((ticker.upper(), action))


def _exp_weight(age_days: float, halflife_days: float = _DECAY_HALFLIFE_DAYS) -> float:
    """Decay weight for an outcome of a given age."""
    if halflife_days <= 0:
        return 1.0
    return 0.5 ** (age_days / halflife_days)


def _win(action: str, outcome_pct: float) -> bool:
    """Return True if this resolved outcome counts as a win for the action."""
    if action == "BUY":
        return outcome_pct > 0
    if action == "SELL":
        return outcome_pct < 0
    return False


def compute_snapshot(
    rows: list[tuple[str, str, float, datetime]],
    *,
    window_days: int = _WINDOW_DAYS,
    decay_halflife_days: float = _DECAY_HALFLIFE_DAYS,
    reference_time: datetime | None = None,
) -> TickerPerformanceSnapshot:
    """Build a ticker-performance snapshot from resolved signal rows.

    Parameters
    ----------
    rows:
        List of (ticker, action, outcome_pct, created_at).  Only BUY/SELL
        actions are meaningful.
    window_days:
        How far back to include outcomes.
    decay_halflife_days:
        Half-life for exponential time decay.
    reference_time:
        Anchor for age calculations; defaults to UTC now.

    Returns
    -------
    TickerPerformanceSnapshot with per-(ticker, action) statistics.
    """
    reference_time = reference_time or datetime.now(timezone.utc)
    cutoff = reference_time - timedelta(days=window_days)

    grouped: dict[tuple[str, str], list[tuple[float, datetime, bool]]] = {}
    for ticker, action, outcome_pct, created_at in rows:
        if action not in ("BUY", "SELL"):
            continue
        if created_at is None or created_at < cutoff:
            continue
        key = (ticker.upper(), action)
        grouped.setdefault(key, []).append(
            (
                float(outcome_pct),
                created_at.replace(tzinfo=timezone.utc) if created_at.tzinfo is None else created_at,
                _win(action, outcome_pct),
            )
        )

    tickers: dict[tuple[str, str], dict] = {}
    total_n = 0
    for key, outcomes in grouped.items():
        total_n += len(outcomes)
        wins = [o[2] for o in outcomes]
        raw_wr = sum(wins) / len(wins) if wins else 0.0

        # Decay weight by age.
        weights = [
            _exp_weight((reference_time - o[1]).total_seconds() / 86400.0, decay_halflife_days) for o in outcomes
        ]
        weighted_wins = sum(w for w, o in zip(weights, outcomes) if o[2])
        weighted_total = sum(weights)
        decay_wr = weighted_wins / weighted_total if weighted_total > 0 else raw_wr

        avg_outcome = sum(o[0] for o in outcomes) / len(outcomes)
        last_at = max(o[1] for o in outcomes)

        tickers[key] = {
            "n": len(outcomes),
            "raw_win_rate": raw_wr,
            "decay_win_rate": decay_wr,
            "avg_outcome": avg_outcome,
            "last_outcome_at": last_at,
            "weights_sum": weighted_total,
        }

    return TickerPerformanceSnapshot(
        tickers=tickers,
        total_n=total_n,
        computed_at=reference_time,
        window_days=window_days,
    )


# ── Cache management ─────────────────────────────────────────────────────────


def cache_snapshot(snapshot: TickerPerformanceSnapshot | None) -> None:
    """Install a snapshot into the in-memory cache (used by tests / refresh)."""
    _CACHE["snapshot"] = snapshot
    _CACHE["loaded_at"] = time.time()


def get_snapshot() -> TickerPerformanceSnapshot | None:
    """Return the cached snapshot, or None if not loaded."""
    return _CACHE.get("snapshot")


def set_disk_load_enabled(enabled: bool) -> None:  # pragma: no cover
    """No-op placeholder: disk persistence can be added when needed."""
    _CACHE["disk_load_enabled"] = enabled


async def refresh_snapshot(db, window_days: int = _WINDOW_DAYS) -> TickerPerformanceSnapshot:
    """Recompute the ticker-performance snapshot from the DB.

    Safe to call from a background job or on startup.  On failure it logs and
    returns the previous cached snapshot (or an empty one) so callers never break.
    """
    try:
        from models import Signal

        reference = datetime.now(timezone.utc)
        cutoff = reference - timedelta(days=window_days)
        result = await db.execute(
            select(Signal.ticker, Signal.action, Signal.outcome_pct, Signal.created_at).where(
                Signal.outcome_pct.isnot(None),
                Signal.created_at >= cutoff,
                Signal.action.in_(("BUY", "SELL")),
            )
        )
        rows = [(r[0], r[1], r[2], r[3]) for r in result.all()]
        snap = compute_snapshot(rows, window_days=window_days, reference_time=reference)
        cache_snapshot(snap)
        log.info(
            "[ticker_perf] refreshed: tickers=%d total_n=%d window=%dd",
            len(snap.tickers),
            snap.total_n,
            window_days,
        )
        return snap
    except Exception:
        log.warning("[ticker_perf] refresh failed; keeping previous snapshot", exc_info=True)
        return get_snapshot() or TickerPerformanceSnapshot({}, 0, datetime.now(timezone.utc), window_days)


# ── Gate ─────────────────────────────────────────────────────────────────────


class TickerPerformanceGate(GateBase):
    """Block or size-reduce tickers with poor recent forward performance.

    Parameters
    ----------
    enabled:
        If False, the gate runs in **shadow mode**: it appends an informational
        rationale card but never blocks or changes size.  This lets the gate be
        compared against the legacy static blocklist before promotion.
    version:
        Gate version string for telemetry.
    """

    version = "1.0"
    expected_impact = "block"
    retirement_rule = (
        "Remove when the ticker shows decay-weighted WR >= 50% over the next "
        f"{_WINDOW_DAYS}-day window with n >= {_MIN_N_BLOCK}, or when a broader "
        "cohort-edge gate supersedes per-ticker blocking."
    )

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def _decide(self, ctx: SignalContext) -> TickerPerformanceDecision:
        """Pure decision logic; does not mutate context."""
        if ctx.action not in ("BUY", "SELL"):
            return TickerPerformanceDecision(False, 1.0, "action is HOLD", 0, 0.0, 0.0, "none", "not_applicable")

        snap = get_snapshot()
        if snap is None:
            return TickerPerformanceDecision(
                False,
                1.0,
                "no performance snapshot available",
                0,
                0.0,
                0.0,
                f"{ctx.ticker}/{ctx.action}",
                "snapshot_unavailable",
            )

        stats = snap.get(ctx.ticker, ctx.action)
        if stats is None:
            return TickerPerformanceDecision(
                False,
                1.0,
                "no recent resolved signals for ticker",
                0,
                0.0,
                0.0,
                f"{ctx.ticker}/{ctx.action}",
                "not_enough_samples",
            )

        n = stats["n"]
        decay_wr = stats["decay_win_rate"]
        raw_wr = stats["raw_win_rate"]
        key = f"{ctx.ticker}/{ctx.action}"

        # Viability guard: very low ATR rank means the signal is already low-
        # confidence on friction grounds.  Prefer a size reduction to a hard block
        # so we don't throw away sparse samples.
        atr_pct_rank = float((ctx.tech or {}).get("atr_pct_rank") or 50.0)
        low_atr = atr_pct_rank < _ATR_RANK_FLOOR

        if n >= _MIN_N_BLOCK and decay_wr < _BLOCK_THRESHOLD:
            if low_atr:
                return TickerPerformanceDecision(
                    False,
                    _CAUTION_SIZE_MULT,
                    f"decay WR {decay_wr:.0%} < {_BLOCK_THRESHOLD:.0%} but ATR rank {atr_pct_rank:.0f} < {_ATR_RANK_FLOOR} → size reduction",
                    n,
                    decay_wr,
                    raw_wr,
                    key,
                    f"forward n={n}",
                )
            return TickerPerformanceDecision(
                True,
                1.0,
                f"decay WR {decay_wr:.0%} < {_BLOCK_THRESHOLD:.0%} (n={n})",
                n,
                decay_wr,
                raw_wr,
                key,
                f"forward n={n}",
            )

        if n >= _MIN_N_CAUTION and decay_wr < _CAUTION_THRESHOLD:
            return TickerPerformanceDecision(
                False,
                _CAUTION_SIZE_MULT,
                f"decay WR {decay_wr:.0%} < {_CAUTION_THRESHOLD:.0%} (n={n}) → size reduction",
                n,
                decay_wr,
                raw_wr,
                key,
                f"forward n={n}",
            )

        return TickerPerformanceDecision(
            False,
            1.0,
            f"decay WR {decay_wr:.0%} above threshold (n={n})",
            n,
            decay_wr,
            raw_wr,
            key,
            f"forward n={n}",
        )

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return

        decision = self._decide(ctx)

        # Shadow mode: only log and add a rationale card.
        if not self.enabled:
            if decision.n > 0:
                ctx.rationale.append(
                    {
                        "src": "Risk Gate",
                        "head": f"Ticker Performance Gate (shadow) — {ctx.ticker}: {decision.reason}",
                        "body": (
                            f"Point-in-time ticker performance gate evaluated {ctx.ticker} "
                            f"over the last {_WINDOW_DAYS} days. "
                            f"{decision.reason}. "
                            "This gate is in shadow mode; the legacy static blocklist "
                            "still governs delivery."
                        ),
                        "sentiment": "neu",
                        "meta": (
                            f"gate=TickerPerformanceGate shadow=true n={decision.n} "
                            f"decay_wr={decision.win_rate:.2f} raw_wr={decision.raw_wr:.2f} "
                            f"validation_type={decision.validation_type}"
                        ),
                    }
                )
                ctx.sources.add("Risk Gate")
            return

        # Enabled: block or size-reduce.
        if decision.block:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Ticker Performance Gate — {ctx.ticker} Blocked",
                    "body": (
                        f"{ctx.ticker} BUY signals have a poor recent track record: "
                        f"{decision.reason}. This ticker is blocked until forward "
                        "performance improves (auto-retirement)."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"gate=TickerPerformanceGate n={decision.n} "
                        f"decay_wr={decision.win_rate:.2f} raw_wr={decision.raw_wr:.2f} "
                        f"validation_type={decision.validation_type}"
                    ),
                }
            )
            return

        if decision.size_mult < 1.0:
            # Apply sizing reduction.  SignalContext currently does not carry
            # position_size_scale, so we append a rationale card noting the
            # recommendation.  The assembler sizing stack can consume this in
            # Stage C via ctx.position_size_scale.
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Ticker Performance Gate — {ctx.ticker} Size ×{decision.size_mult:.0%}",
                    "body": (
                        f"{ctx.ticker} BUY signals are marginal: {decision.reason}. "
                        f"Recommended position size reduced to {decision.size_mult:.0%} of normal."
                    ),
                    "sentiment": "neg",
                    "meta": (
                        f"gate=TickerPerformanceGate n={decision.n} "
                        f"decay_wr={decision.win_rate:.2f} raw_wr={decision.raw_wr:.2f} "
                        f"size_mult={decision.size_mult} "
                        f"validation_type={decision.validation_type}"
                    ),
                }
            )
            ctx.sources.add("Risk Gate")
