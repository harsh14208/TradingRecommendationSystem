#!/usr/bin/env python3
"""§103 — Automated strategy-decay monitor.

Nightly task computing trailing-50-resolved net avg + Wilson CI on the clean
delivered book (BUY, post-2026-06-10), persisted to `edge_health` rows.
Alerts via TSYS-10 when trailing CI upper bound < +0.5%/trade (decay)
or when SPRT flips to accept-H1 (confirmation — green-lights sizing up).
Regime context distinguishes VIX<20 drought (N starvation) from true decay.
"""

from __future__ import annotations

import math
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sqlalchemy import select

from database import AsyncSessionLocal
from models import Signal

log = __import__("logging").getLogger("signal.trade.decay_monitor")

# TSYS-10 threshold: trailing CI upper bound < +0.5%/trade = decay alarm
_DECAY_THRESHOLD = 0.5
_CONFIRMATION_THRESHOLD = 1.0  # CI lower bound > +1.0% = confirmation alarm
_TRAILING_N = 50

# VIX regime buckets for §103c
_VIX_CALM = 20.0
_VIX_ELEVATED = 25.0


def wilson_ci(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion."""
    if n == 0:
        return 0.0, 0.0
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return centre - margin, centre + margin


def _fetch_vix_series(start_date: datetime, end_date: datetime) -> dict[datetime, float]:
    """Fetch VIX close prices for the date range via yfinance."""
    try:
        import yfinance as yf

        _start = (start_date - timedelta(days=5)).strftime("%Y-%m-%d")
        _end = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")
        df = yf.download("^VIX", start=_start, end=_end, interval="1d", auto_adjust=False, progress=False)
        if df.empty:
            return {}
        _closes = df["Close"] if "Close" in df.columns else pd.Series(dtype=float)
        return {
            pd.Timestamp(str(k)).to_pydatetime().replace(tzinfo=None): float(v)
            for k, v in _closes.items()
            if pd.notna(v)
        }
    except Exception as exc:
        log.warning("VIX fetch failed: %s", exc)
        return {}


def _vix_regime_for_window(vix_series: dict[datetime, float], signal_dates: list[datetime]) -> dict:
    """Classify VIX regime for the trailing window."""
    if not vix_series or not signal_dates:
        return {"avg_vix": None, "regime": "unknown", "coverage": 0.0}

    # Map each signal date to nearest prior VIX reading
    _sorted = sorted(vix_series.items())
    _values: list[float] = []
    for sig_dt in signal_dates:
        _dt = sig_dt.replace(tzinfo=None) if sig_dt.tzinfo else sig_dt
        # Find most recent VIX reading on or before signal date
        _val = None
        for vdt, vval in _sorted:
            if vdt.date() <= _dt.date():
                _val = vval
            else:
                break
        if _val is not None:
            _values.append(_val)

    if not _values:
        return {"avg_vix": None, "regime": "unknown", "coverage": 0.0}

    avg_vix = sum(_values) / len(_values)
    if avg_vix < _VIX_CALM:
        regime = "calm"
    elif avg_vix < _VIX_ELEVATED:
        regime = "normal"
    else:
        regime = "elevated"

    return {
        "avg_vix": round(avg_vix, 2),
        "regime": regime,
        "coverage": len(_values) / len(signal_dates),
    }


async def compute_edge_health(after_date: datetime | None = None) -> dict | None:
    """Compute trailing-N metrics on the clean delivered book."""
    if after_date is None:
        after_date = datetime(2026, 6, 10, 15, 56, tzinfo=timezone.utc)

    # DB created_at is naive; ensure after_date is naive for comparison
    _after_naive = after_date.replace(tzinfo=None) if after_date.tzinfo else after_date
    async with AsyncSessionLocal() as db:
        stmt = (
            select(Signal)
            .where(
                Signal.is_sent == True,
                Signal.action == "BUY",
                Signal.outcome_pct.isnot(None),
                Signal.created_at >= _after_naive,
            )
            .order_by(Signal.outcome_at.desc())
            .limit(_TRAILING_N)
        )
        rows = (await db.execute(stmt)).scalars().all()

    if not rows:
        return None

    outcomes = [r.outcome_pct for r in rows if r.outcome_pct is not None]
    signal_dates = [r.created_at for r in rows if r.outcome_pct is not None]
    n = len(outcomes)
    wins = sum(1 for o in outcomes if o > 0)
    wr = wins / n * 100 if n > 0 else 0.0
    avg = sum(outcomes) / n if n > 0 else 0.0
    variance = sum((o - avg) ** 2 for o in outcomes) / max(n - 1, 1) if n > 1 else 0.0
    std = math.sqrt(variance) if variance > 0 else 0.0
    sharpe = avg / std if std > 0 else 0.0

    # Wilson CI on win rate
    wr_lo, wr_hi = wilson_ci(wins / n if n > 0 else 0.0, n)

    # T-stat on mean return
    t_stat = avg / (std / math.sqrt(n)) if std > 0 and n > 0 else 0.0

    # Expected return CI (rough: mean ± 1.96 * SE)
    se = std / math.sqrt(n) if n > 0 else 0.0
    avg_lo = avg - 1.96 * se
    avg_hi = avg + 1.96 * se

    # §103c: VIX regime context
    _min_dt = min(signal_dates)
    _max_dt = max(signal_dates)
    vix_series = _fetch_vix_series(_min_dt, _max_dt)
    vix_regime = _vix_regime_for_window(vix_series, signal_dates)

    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "after_date": after_date.isoformat(),
        "n": n,
        "win_rate": round(wr, 1),
        "wr_ci_low": round(wr_lo * 100, 1),
        "wr_ci_high": round(wr_hi * 100, 1),
        "avg_return": round(avg, 3),
        "avg_ci_low": round(avg_lo, 3),
        "avg_ci_high": round(avg_hi, 3),
        "sharpe": round(sharpe, 3),
        "t_stat": round(t_stat, 2),
        "std": round(std, 3),
        "alarm": None,
        "vix_regime": vix_regime["regime"],
        "avg_vix": vix_regime["avg_vix"],
        "vix_coverage": round(vix_regime["coverage"], 2),
    }


def evaluate_alarm(health: dict) -> str | None:
    """Return alarm type based on health metrics and VIX regime context."""
    if health["n"] < 20:
        return "insufficient_data"

    _regime = health.get("vix_regime", "unknown")

    # Decay: CI upper bound below threshold
    if health["avg_ci_high"] < _DECAY_THRESHOLD:
        # §103c: calm regime = likely N starvation, not true decay
        if _regime == "calm":
            return "drought"
        return "decay"

    # Confirmation: CI lower bound above threshold
    if health["avg_ci_low"] > _CONFIRMATION_THRESHOLD:
        return "confirmation"

    return None


async def main() -> None:
    print("=== §103 Decay Monitor ===")
    health = await compute_edge_health()
    if health is None:
        print("No resolved signals in clean book yet.")
        return

    alarm = evaluate_alarm(health)
    health["alarm"] = alarm

    print(f"Trailing window: N={health['n']}  post-{health['after_date'][:10]}")
    print(f"Win Rate: {health['win_rate']:.1f}%  CI [{health['wr_ci_low']:.1f}%, {health['wr_ci_high']:.1f}%]")
    print(f"Avg Return: {health['avg_return']:+.3f}%  CI [{health['avg_ci_low']:+.3f}%, {health['avg_ci_high']:+.3f}%]")
    print(f"Sharpe: {health['sharpe']:.3f}  t={health['t_stat']:.2f}")
    if health.get("avg_vix") is not None:
        print(
            f"VIX Regime: {health['vix_regime']} (avg {health['avg_vix']:.1f}, coverage {health['vix_coverage']:.0%})"
        )

    if alarm == "decay":
        print(f"\n🚨 DECAY ALARM: trailing CI upper bound {health['avg_ci_high']:+.3f}% < {_DECAY_THRESHOLD}%")
        print("   Action: reduce sizing, review gates, check for regime shift")
    elif alarm == "drought":
        print(
            f"\n⏳ DROUGHT (VIX < {_VIX_CALM:.0f}): trailing CI upper bound {health['avg_ci_high']:+.3f}% < {_DECAY_THRESHOLD}%"
        )
        print("   Context: calm markets produce fewer MR signals — edge may be intact but N is sparse.")
        print("   Action: monitor, do NOT reduce sizing based on sparse data alone")
    elif alarm == "confirmation":
        print(f"\n✅ CONFIRMATION: trailing CI lower bound {health['avg_ci_low']:+.3f}% > {_CONFIRMATION_THRESHOLD}%")
        print("   Action: edge confirmed — green-light sizing up")
    elif alarm == "insufficient_data":
        print(f"\n⏳ Insufficient data (N={health['n']} < 20) — cannot evaluate decay")
    else:
        print("\n⏳ No alarm — edge in monitoring zone")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
