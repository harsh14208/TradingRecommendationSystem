"""
Empirical confidence calibration (bin-based Platt-style).

Reads resolved signals from the DB, groups by 5pp confidence bin, computes
the actual win rate per bin, then blends the model confidence toward the
empirical win rate proportionally to how many samples are in that bin.

  calibrated = emp_win_rate * blend + raw_confidence * (1 - blend)

blend = min(0.80, n_samples / 30)   →  0.0 with <1 sample, ≈0.80 with ≥24

Results are written to backend/data/calibration.json and returned as a dict
that the scanner injects into market_ctx["calibration_map"] every scan cycle.
"""
import json
import logging
import os
from collections import defaultdict
from pathlib import Path

log = logging.getLogger("signal.trade.calibration")

_DATA_DIR  = Path(__file__).parent.parent / "data"
_CAL_FILE  = _DATA_DIR / "calibration.json"
_BIN_SIZE  = 5          # pp width of each confidence bin
_MIN_N     = 3          # minimum samples before blending activates
_MAX_BLEND = 0.90       # trust empirical data up to 90% (tightened from 80%)
_N_FULL    = 20         # samples at which blend reaches MAX_BLEND (lowered from 30)


def _blend(n: int) -> float:
    if n < _MIN_N:
        return 0.0
    return min(_MAX_BLEND, n / _N_FULL)


async def run_calibration() -> dict:
    """
    Compute calibration map from resolved sent signals.
    Returns the map and writes it to disk.
    """
    try:
        from sqlalchemy import select
        from database import AsyncSessionLocal
        from models import Signal

        async with AsyncSessionLocal() as db:
            rows = (await db.execute(
                select(Signal.action, Signal.confidence, Signal.outcome_14d, Signal.outcome_pct)
                .where(Signal.is_sent    == True)
                .where(Signal.action.in_(["BUY", "SELL"]))
                .where(
                    (Signal.outcome_14d.isnot(None)) | (Signal.outcome_pct.isnot(None))
                )
            )).all()

        if not rows:
            log.info("[calibration] no resolved signals — skipping")
            return {}

        # Bin → {wins, total}
        # Prefer outcome_14d; fall back to outcome_pct (7d) when 14d not yet available.
        bins: dict[int, dict] = defaultdict(lambda: {"wins": 0, "total": 0})
        for action, conf, pct_14d, pct_7d in rows:
            pct = pct_14d if pct_14d is not None else pct_7d
            if pct is None:
                continue
            b = (int(conf) // _BIN_SIZE) * _BIN_SIZE
            b = max(0, min(95, b))
            bins[b]["total"] += 1
            win = (pct > 0 if action == "BUY" else pct < 0)
            if win:
                bins[b]["wins"] += 1

        cal_map: dict[str, dict] = {}
        for b, stats in sorted(bins.items()):
            n  = stats["total"]
            wr = stats["wins"] / n if n > 0 else 0.5
            cal_map[str(b)] = {
                "win_rate": round(wr, 4),
                "n":        n,
                "blend":    round(_blend(n), 3),
            }
            log.debug(
                f"[calibration] bin {b}-{b+_BIN_SIZE}%: "
                f"wr={wr*100:.1f}% n={n} blend={_blend(n):.2f}"
            )

        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        _CAL_FILE.write_text(json.dumps(cal_map, indent=2))
        log.info(
            f"[calibration] wrote {len(cal_map)} bins "
            f"({sum(v['n'] for v in cal_map.values())} resolved signals)"
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


def apply_calibration(
    raw_conf: float, action: str, cal_map: dict
) -> tuple[float, dict | None]:
    """
    Blend raw model confidence toward the empirical win rate for its bin.

    Returns (calibrated_confidence, bin_meta) where bin_meta is the matching
    calibration entry dict (keys: win_rate, n, blend) or None if not applied.
    Calibrated confidence is clamped to [35, 72].
    """
    if not cal_map or action not in ("BUY", "SELL"):
        return raw_conf, None

    b = str(max(0, (int(raw_conf) // _BIN_SIZE) * _BIN_SIZE))
    # Try exact bin; fall back one bin lower only if it's a different key
    _lower = str(max(0, int(b) - _BIN_SIZE))
    entry = cal_map.get(b) or (cal_map.get(_lower) if _lower != b else None)
    if not entry or entry["blend"] == 0.0:
        return raw_conf, None

    emp_wr_pct = entry["win_rate"] * 100
    blend      = entry["blend"]
    calibrated = emp_wr_pct * blend + raw_conf * (1.0 - blend)
    return round(min(72.0, max(35.0, calibrated)), 1), entry
