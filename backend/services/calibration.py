"""
Confidence calibration — v2 (regime-aware, recency-weighted, walk-forward).

Architecture:
  Alpha score   = raw signal score (35–150+) — used for trade ranking / ordering
  Probability   = calibrated win probability (what the user sees as "confidence %")

  These are now separate. The calibration layer is the bridge:
    raw_conf  →  regime-specific isotonic  →  calibrated probability

v1 problems this fixes:
  - _score_to_action() compressed score 35–100 into 58–65% (7pp range)
    → calibration could barely move within that range
    → Brier score 0.2863 (near-random)
  - Single global calibration: bull-market signals and bear-market signals
    treated identically despite having different win rate distributions
  - 65% ceiling clipped the best calibrated signals to 65% even when
    empirical win rate was 75%+
  - No recency weighting: 18-day-old signals counted same as yesterday's

v2 changes:
  1. Regime-aware isotonic  — separate curves for bull / bear / neutral
     derived from SPY-SMA200 trend at signal creation time
  2. Recency weighting      — exponential decay, half-life 45 days
  3. Walk-forward Brier     — train on 80%, validate on 20%, score stored in _meta
  4. Wider confidence cap   — 78% (calibration sets it, not a hard ceiling)
  5. Brier score output     — tracked in _meta so quality is measurable
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("signal.trade.calibration")

_DATA_DIR = Path(__file__).parent.parent / "data"
_CAL_FILE = _DATA_DIR / "calibration.json"
_BIN_SIZE = 5  # pp bin width for Platt fallback
_MIN_N = 3  # min samples before blending
_MAX_BLEND = 0.97  # empirical weight ceiling
_N_FULL = 15  # reach MAX_BLEND at this sample count
_HALF_LIFE = 45.0  # recency decay half-life in days
_CONF_FLOOR = 35.0  # minimum output confidence
_CONF_CEIL = 78.0  # maximum output confidence — raised from 65% (v1 ceiling
# clipped calibrated 75%+ WR signals to 65%)
_VALID_FRAC = 0.20  # fraction held out for walk-forward Brier scoring


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _blend(n: int) -> float:
    if n < _MIN_N:
        return 0.0
    return min(_MAX_BLEND, n / _N_FULL)


def _recency_weight(created_at: datetime | None, ref_dt: datetime | None = None) -> float:
    """Exponential decay weight: 1.0 at 0 days ago, 0.5 at HALF_LIFE days ago."""
    if created_at is None:
        return 1.0
    ref = ref_dt or datetime.now(timezone.utc)
    # Ensure both are offset-aware
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    days_ago = max(0.0, (ref - created_at).total_seconds() / 86400.0)
    return math.exp(-math.log(2) / _HALF_LIFE * days_ago)


def _fit_isotonic(X: list, y: list, w: list | None = None) -> list | None:
    """Fit isotonic regression; return (conf, prob) table or None."""
    if len(X) < 20:
        return None
    try:
        import numpy as np
        from sklearn.isotonic import IsotonicRegression

        ir = IsotonicRegression(out_of_bounds="clip", increasing=True)
        ir.fit(X, y, sample_weight=w if w else None)
        confs = np.linspace(_CONF_FLOOR / 100, _CONF_CEIL / 100, 44)
        probs = ir.predict(confs)
        return [[round(float(c), 3), round(float(p), 4)] for c, p in zip(confs, probs)]
    except Exception as exc:
        log.debug(f"[calibration] isotonic fit failed: {exc}")
        return None


def _brier_score(probs: list[float], wins: list[int]) -> float:
    """Mean squared error between predicted probabilities and binary outcomes."""
    if not probs:
        return float("nan")
    return round(sum((p - y) ** 2 for p, y in zip(probs, wins)) / len(probs), 4)


def _interp_isotonic(table: list, x: float) -> float | None:
    """Linear interpolation over a sorted (conf, prob) table."""
    if not table or len(table) < 2:
        return None
    for i in range(len(table) - 1):
        c0, p0 = table[i]
        c1, p1 = table[i + 1]
        if c0 <= x <= c1:
            t = (x - c0) / (c1 - c0) if c1 > c0 else 0.0
            return p0 + t * (p1 - p0)
    # Clamp to edges
    if x < table[0][0]:
        return table[0][1]
    return table[-1][1]


def _spy_regime_at(created_at: datetime, spy_cache: dict) -> str:
    """Return 'bull' / 'bear' / 'neutral' from cached SPY→SMA200 trend."""
    if not spy_cache:
        return "neutral"
    date_key = created_at.strftime("%Y-%m-%d")
    return spy_cache.get(date_key, "neutral")


def _build_spy_regime_cache(start: str, end: str) -> dict:
    """
    Download SPY close prices and compute bull/bear/neutral for each date.
    Returns {date_str: regime_str}.
    """
    try:
        import pandas as pd
        import yfinance as yf

        raw = yf.download("SPY", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        closes = raw["Close"].ffill()
        sma200 = closes.rolling(200).mean()
        cache = {}
        for dt, c, s in zip(closes.index, closes.values, sma200.values):
            if not isinstance(s, float) or s != s:
                continue
            ratio = float(c) / float(s)
            if ratio > 1.02:
                regime = "bull"
            elif ratio < 0.98:
                regime = "bear"
            else:
                regime = "neutral"
            cache[str(dt)[:10]] = regime
        return cache
    except Exception as exc:
        log.debug(f"[calibration] SPY regime cache failed: {exc}")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Main calibration run
# ─────────────────────────────────────────────────────────────────────────────


async def run_calibration() -> dict:
    """
    Build a regime-aware, recency-weighted calibration map from resolved signals.

    Win labels are net-of-friction (deducting a 0.50% round-trip cost) so that
    calibrated probabilities answer "P(profitable trade)" rather than
    "P(gross-positive at an inconsistent horizon)". The canonical hold horizon
    is ~10 days; we evaluate profitability after friction.

    Writes calibration.json and returns the map.
    """
    try:
        from database import AsyncSessionLocal
        from models import Signal
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            rows = (
                await db.execute(
                    select(
                        Signal.action,
                        Signal.confidence,
                        Signal.outcome_14d,
                        Signal.outcome_pct,
                        Signal.created_at,
                    )
                    .where(Signal.is_sent == True)
                    .where(Signal.action.in_(["BUY", "SELL"]))
                    .where((Signal.outcome_14d.isnot(None)) | (Signal.outcome_pct.isnot(None)))
                    .order_by(Signal.created_at)
                )
            ).all()

        if not rows:
            log.info("[calibration] no resolved signals — skipping")
            return {}

        # ── Extract date range for SPY regime cache ───────────────────────────
        dates = [r.created_at for r in rows if r.created_at]
        if dates:
            start = min(dates).strftime("%Y-%m-%d")
            end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        else:
            start, end = "2024-01-01", datetime.now(timezone.utc).strftime("%Y-%m-%d")

        spy_cache = _build_spy_regime_cache(start, end)
        log.info(f"[calibration] SPY regime cache: {len(spy_cache)} dates")

        # ── Compile samples ───────────────────────────────────────────────────
        ref_dt = datetime.now(timezone.utc)
        samples = []
        for action, conf, pct_14d, pct_7d, created_at in rows:
            pct = pct_14d if pct_14d is not None else pct_7d
            if pct is None:
                continue
            # Net-of-friction win label: must clear 0.50% round-trip cost.
            # The strategy's canonical hold is 10 days; we evaluate profitability
            # after friction, not gross positivity.
            net_pct = pct - 0.50
            win = 1 if (net_pct > 0 if action == "BUY" else net_pct < 0) else 0
            weight = _recency_weight(created_at, ref_dt)
            regime = _spy_regime_at(created_at, spy_cache) if created_at else "neutral"
            samples.append(
                {
                    "conf": conf,
                    "win": win,
                    "weight": weight,
                    "regime": regime,
                    "created": created_at,
                }
            )

        n_total = len(samples)
        if n_total == 0:
            return {}

        # ── Walk-forward split: train 80%, validate 20% (most-recent) ─────────
        split = max(1, int(n_total * (1 - _VALID_FRAC)))
        train = samples[:split]
        valid = samples[split:]

        # ── Global calibration (Platt bins on train set) ──────────────────────
        bins: dict[int, dict] = defaultdict(lambda: {"w_wins": 0.0, "w_total": 0.0})
        for s in train:
            b = max(0, min(95, (int(s["conf"]) // _BIN_SIZE) * _BIN_SIZE))
            bins[b]["w_total"] += s["weight"]
            bins[b]["w_wins"] += s["weight"] * s["win"]

        cal_map: dict[str, object] = {}
        for b, bstats in sorted(bins.items()):
            wt = bstats["w_total"]
            wr = bstats["w_wins"] / wt if wt > 0 else 0.5
            n_raw = sum(1 for s in train if max(0, min(95, (int(s["conf"]) // _BIN_SIZE) * _BIN_SIZE)) == b)
            cal_map[str(b)] = {
                "win_rate": round(wr, 4),
                "n": n_raw,
                "blend": round(_blend(n_raw), 3),
            }
            log.debug(f"[calibration] bin {b}: wr={wr * 100:.1f}% n={n_raw} w={wt:.1f}")

        # ── Global isotonic (recency-weighted) ────────────────────────────────
        _X = [s["conf"] / 100.0 for s in train]
        _y = [s["win"] for s in train]
        _w = [s["weight"] for s in train]
        iso_global = _fit_isotonic(_X, _y, _w)
        if iso_global:
            cal_map["_isotonic"] = iso_global
            log.info(f"[calibration] global isotonic fitted on {len(_X)} samples")

        # ── Regime-specific isotonic ─────────────────────────────────────────
        regime_map: dict[str, dict] = {}
        for regime in ("bull", "bear", "neutral"):
            sub = [s for s in train if s["regime"] == regime]
            if len(sub) < 20:
                log.debug(f"[calibration] {regime}: only {len(sub)} samples — skip")
                continue
            rx = [s["conf"] / 100.0 for s in sub]
            ry = [s["win"] for s in sub]
            rw = [s["weight"] for s in sub]
            iso = _fit_isotonic(rx, ry, rw)
            # Platt bins per regime
            rbins: dict[int, dict] = defaultdict(lambda: {"w_wins": 0.0, "w_total": 0.0})
            for s in sub:
                b = max(0, min(95, (int(s["conf"]) // _BIN_SIZE) * _BIN_SIZE))
                rbins[b]["w_total"] += s["weight"]
                rbins[b]["w_wins"] += s["weight"] * s["win"]
            rbin_map = {}
            for b, bst in sorted(rbins.items()):
                wt = bst["w_total"]
                wr = bst["w_wins"] / wt if wt > 0 else 0.5
                n_r = sum(1 for s in sub if max(0, min(95, (int(s["conf"]) // _BIN_SIZE) * _BIN_SIZE)) == b)
                rbin_map[str(b)] = {"win_rate": round(wr, 4), "n": n_r, "blend": round(_blend(n_r), 3)}
            regime_entry: dict = {"n": len(sub), "bins": rbin_map}
            if iso:
                regime_entry["_isotonic"] = iso
            regime_map[regime] = regime_entry
            log.info(f"[calibration] {regime} isotonic: {len(sub)} samples")
        if regime_map:
            cal_map["_regime"] = regime_map

        # ── Walk-forward Brier score (validation set) ─────────────────────────
        if valid:
            preds, actuals = [], []
            for s in valid:
                # Predict using global isotonic or Platt
                x = s["conf"] / 100.0
                if iso_global:
                    p = _interp_isotonic(iso_global, x)
                    if p is not None:
                        preds.append(p)
                        actuals.append(s["win"])
                        continue
                # Platt fallback
                b = str(max(0, min(95, (int(s["conf"]) // _BIN_SIZE) * _BIN_SIZE)))
                entry = cal_map.get(b)
                if entry and isinstance(entry, dict) and entry.get("blend", 0) > 0:
                    p = entry["win_rate"] * entry["blend"] + s["conf"] / 100 * (1 - entry["blend"])
                    preds.append(p)
                    actuals.append(s["win"])
            brier = _brier_score(preds, actuals)
            brier_naive = _brier_score([0.5] * len(actuals), actuals)  # baseline: predict 50%
            log.info(
                f"[calibration] Brier (walk-forward, n={len(preds)}): {brier:.4f} vs naive 0.5 → {brier_naive:.4f}"
            )
        else:
            brier = float("nan")

        # ── Regime counts & metadata ──────────────────────────────────────────
        regime_counts = defaultdict(int)
        for s in samples:
            regime_counts[s["regime"]] += 1

        meta = {
            "n_total": n_total,
            "n_train": len(train),
            "n_valid": len(valid),
            "n_bull": regime_counts["bull"],
            "n_bear": regime_counts["bear"],
            "n_neutral": regime_counts["neutral"],
            "brier_walkforward": brier if not (isinstance(brier, float) and brier != brier) else None,
            "brier_naive_50pct": round(brier_naive, 4) if valid else None,
            "last_run": datetime.now(timezone.utc).isoformat()[:19],
            "conf_floor": _CONF_FLOOR,
            "conf_ceil": _CONF_CEIL,
        }

        # Self-gate: only deploy a calibration that demonstrably beats the naive
        # 50% baseline. A no-skill / over-pessimistic map (Brier ≥ naive) flattens
        # confidence toward the base win-rate, which can fall below the delivery
        # floor and silently zero out ALL signal delivery (observed 2026-06-15:
        # isotonic collapsed to a flat 42.8%, below the 46% swing floor → 0 sends).
        # When that happens we persist a no-op map (only _meta) so apply_calibration
        # passes raw confidence through instead of suppressing every signal.
        skilled = isinstance(brier, float) and brier == brier and bool(valid) and brier < brier_naive
        if not skilled:
            meta["applied"] = False
            meta["reason"] = (
                f"no skill (Brier {brier:.4f} ≥ naive {brier_naive:.4f}) — raw confidence passed through"
                if (isinstance(brier, float) and brier == brier and valid)
                else "insufficient validation data — raw confidence passed through"
            )
            cal_map = {"_meta": meta}
            log.warning(f"[calibration] NOT deployed: {meta['reason']}")
        else:
            meta["applied"] = True
            cal_map["_meta"] = meta

        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        _CAL_FILE.write_text(json.dumps(cal_map, indent=2))
        log.info(
            f"[calibration] wrote {n_total} signals · "
            f"bull={regime_counts['bull']} bear={regime_counts['bear']} "
            f"neutral={regime_counts['neutral']} · Brier={brier:.4f}"
            if isinstance(brier, float) and brier == brier
            else f"neutral={regime_counts['neutral']} · Brier=n/a"
        )
        return cal_map

    except Exception as exc:
        log.warning(f"[calibration] failed: {exc}")
        return {}


def load_calibration() -> dict:
    """Load calibration map from disk (used at scanner startup)."""
    try:
        if _CAL_FILE.exists():
            return json.loads(_CAL_FILE.read_text())
    except Exception:
        pass
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# TSYS-7d — calibration rollback
# ─────────────────────────────────────────────────────────────────────────────


async def archive_current_calibration(db) -> str:
    """Snapshot the on-disk calibration into CalibrationHistory and mark it active.

    Returns the archived version string. Idempotent per version (same last_run is
    not re-archived). Call after writing a new calibration so a prior good curve
    can be restored if the new one degrades live performance.
    """
    from sqlalchemy import update

    from models import CalibrationHistory

    cal = load_calibration()
    if not cal:
        return ""
    version = str(cal.get("last_run") or datetime.now(timezone.utc).isoformat()[:19])

    from sqlalchemy import select

    existing = (
        await db.execute(select(CalibrationHistory).where(CalibrationHistory.version == version))
    ).scalar_one_or_none()
    if existing is not None:
        return version

    await db.execute(update(CalibrationHistory).values(is_active=False))
    db.add(CalibrationHistory(version=version, calibration_data=cal, is_active=True))
    await db.commit()
    log.info(f"[calibration] archived version {version}")
    return version


async def restore_calibration_version(db, version: str) -> bool:
    """TSYS-7d: restore a previously archived calibration to disk and mark active.

    Returns True on success, False if the version does not exist.
    """
    from sqlalchemy import select, update

    from models import CalibrationHistory

    row = (
        await db.execute(select(CalibrationHistory).where(CalibrationHistory.version == version))
    ).scalar_one_or_none()
    if row is None:
        return False

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _CAL_FILE.write_text(json.dumps(row.calibration_data, indent=2))
    await db.execute(update(CalibrationHistory).values(is_active=False))
    row.is_active = True
    await db.commit()
    log.info(f"[calibration] rolled back to version {version}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Apply calibration
# ─────────────────────────────────────────────────────────────────────────────


def apply_calibration(
    raw_conf: float,
    action: str,
    cal_map: dict,
    regime: str | None = None,
) -> tuple[float, dict | None]:
    """
    Map raw model confidence → calibrated win probability.

    Priority order:
      1. Regime-specific isotonic  (if regime provided + ≥20 training samples)
      2. Global isotonic           (if ≥20 training samples available)
      3. Platt bin blend           (fallback)

    Returns (calibrated_confidence %, bin_meta_dict).
    Output is clamped to [_CONF_FLOOR, _CONF_CEIL].
    """
    if not cal_map or action not in ("BUY", "SELL"):
        return raw_conf, None

    x = raw_conf / 100.0

    # ── 1. Regime-specific isotonic ───────────────────────────────────────────
    if regime and "_regime" in cal_map:
        reg_entry = cal_map["_regime"].get(regime, {})
        iso_reg = reg_entry.get("_isotonic")
        if iso_reg and reg_entry.get("n", 0) >= 20:
            p = _interp_isotonic(iso_reg, x)
            if p is not None:
                cal = round(min(_CONF_CEIL, max(_CONF_FLOOR, p * 100)), 1)
                return cal, {"source": f"isotonic_{regime}", "prob": round(p, 4)}

    # ── 2. Global isotonic ────────────────────────────────────────────────────
    iso = cal_map.get("_isotonic")
    if iso and len(iso) >= 10:
        p = _interp_isotonic(iso, x)
        if p is not None:
            cal = round(min(_CONF_CEIL, max(_CONF_FLOOR, p * 100)), 1)
            return cal, {"source": "isotonic_global", "prob": round(p, 4)}

    # ── 3. Platt bin blend (fallback) ─────────────────────────────────────────
    b = str(max(0, (int(raw_conf) // _BIN_SIZE) * _BIN_SIZE))
    _lower = str(max(0, int(b) - _BIN_SIZE))
    entry = cal_map.get(b) or (cal_map.get(_lower) if _lower != b else None)
    if not entry or not isinstance(entry, dict) or entry.get("blend", 0.0) == 0.0:
        return raw_conf, None

    emp_wr_pct = entry["win_rate"] * 100
    blend = entry["blend"]
    calibrated = emp_wr_pct * blend + raw_conf * (1.0 - blend)
    return round(min(_CONF_CEIL, max(_CONF_FLOOR, calibrated)), 1), entry
