"""
Delivery gates — pre-send eligibility checks for every signal.

Each gate returns early with a skip reason string if the signal should not
be delivered. A None return means the signal passed all gates.

Extracted from scanner._maybe_send() so that:
  - Gates are unit-testable in isolation
  - Live broker execution (OAuth path) can run the same gates
  - scanner.py stays focused on orchestration
"""
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

log = logging.getLogger("scanner")

# ── Gate configuration ────────────────────────────────────────────────────────

# Empirical profit factors from 529 resolved live signals (Apr-May 2026):
#   Position: 61.6% WR, +2.88% avg, Sharpe 6.45  → keep flowing
#   Swing:    45.5% WR, +0.81% avg, Sharpe 1.93   → restrict to near-ceiling only
#   Intraday: 34.8% WR, -0.65% avg, Sharpe -1.88  → disabled
# Note: confidence ceiling lowered to 65% in v5.12; intraday floor of 68
# would already block all intraday, but set to 999 to be explicit.
STYLE_CONF_FLOORS: dict[str, float] = {
    "intraday": 999.0,   # DISABLED — 34.8% WR, Sharpe -1.88 (May 2026 live data)
    "swing":    62.0,    # adjusted for new 65% ceiling; only near-ceiling swing setups pass
    "position": 0.0,     # no additional floor — driven by global min_confidence (55%)
}

# Sectors with empirical PF < 0.40x blocked until per-sector models retrained.
# XLF 0.32x, XLP 0.35x, XLU insufficient data.
BLOCKED_SECTORS: frozenset[str] = frozenset({"XLF", "XLP", "XLU"})


async def check_delivery_gates(
    sig_dict: dict,
    db,
    settings,
) -> tuple[str | None, dict]:
    """
    Run all pre-send eligibility gates against sig_dict.

    Returns:
        (skip_reason, sig_dict)
        skip_reason — human-readable string if blocked, else None.
        sig_dict    — possibly mutated copy (holiday haircut may modify confidence).

    The caller should return immediately when skip_reason is not None.
    """
    ticker = sig_dict["ticker"]
    action = sig_dict.get("action", "")
    conf   = sig_dict.get("confidence", 0)

    # ── Action guard ─────────────────────────────────────────────────────────
    if action not in ("BUY", "SELL"):
        return f"action={action} not BUY/SELL", sig_dict

    # ── Global confidence floor ───────────────────────────────────────────────
    if conf < settings.min_confidence:
        return (
            f"conf {conf:.0f}% < global floor {settings.min_confidence:.0f}%",
            sig_dict,
        )

    # ── Style gate ────────────────────────────────────────────────────────────
    style = sig_dict.get("style", "swing")
    style_floor = STYLE_CONF_FLOORS.get(style, 70.0)
    if conf < style_floor:
        return (
            f"{style} style disabled/floored — conf {conf:.0f}% < {style_floor:.0f}%",
            sig_dict,
        )

    # ── Sector gate ───────────────────────────────────────────────────────────
    sector = sig_dict.get("sectorEtf") or sig_dict.get("sector_etf")
    if sector and sector in BLOCKED_SECTORS:
        return (
            f"sector {sector} blocked (low PF) — awaiting retraining",
            sig_dict,
        )

    # ── Pre-earnings blackout (≤2 trading days) ───────────────────────────────
    dte = sig_dict.get("daysToEarnings")
    if dte is not None and 0 < dte <= 2:
        return f"{dte}d to earnings — pre-earnings hard blackout", sig_dict

    # ── Sector concentration limit (max 2 BUY per sector per 24h) ────────────
    if sector and action == "BUY":
        from models import Signal
        cutoff = datetime.utcnow() - timedelta(hours=24)
        count = (await db.execute(
            select(func.count()).select_from(Signal)
            .where(Signal.sector_etf == sector)
            .where(Signal.action     == "BUY")
            .where(Signal.is_sent    == True)
            .where(Signal.sent_at    >= cutoff)
        )).scalar_one()
        if count >= 2:
            return f"sector {sector} already has {count} BUY sends in 24h (max 2)", sig_dict

    # ── Ticker-adaptive confidence floor ──────────────────────────────────────
    try:
        from database import AsyncSessionLocal
        from models import AppSettings
        async with AsyncSessionLocal() as _adb:
            _srow = (await _adb.execute(
                select(AppSettings).where(AppSettings.id == 1)
            )).scalar_one_or_none()
        app_data  = (_srow.data or {}) if _srow else {}
        ticker_wrs = app_data.get("adaptive_weights", {}).get("ticker_win_rates", {})
        twr = ticker_wrs.get(ticker)
        if twr is not None:
            if twr < 0.45 and conf < 68.0:
                return (
                    f"hist win rate {twr*100:.0f}% requires ≥68% conf (got {conf:.0f}%)",
                    sig_dict,
                )
            if twr >= 0.75 and conf < 52.0:
                return (
                    f"high-win ticker {twr*100:.0f}% WR but conf {conf:.0f}% < 52% floor",
                    sig_dict,
                )
    except Exception:
        pass

    # ── Source independence gate ──────────────────────────────────────────────
    sources_set = set(sig_dict.get("sources") or [])
    non_ta = sources_set - {
        "Technical", "Technicals", "Risk Gate", "Backtest",
        "Cross-Sectional", "Orthogonalization", "Signal Cluster",
    }
    min_non_ta = 2 if style == "position" else 1
    if len(non_ta) < min_non_ta:
        return (
            f"only {len(non_ta)} non-TA sources for {style} (need {min_non_ta})",
            sig_dict,
        )

    # ── Minimum profit filter ─────────────────────────────────────────────────
    entry  = sig_dict.get("entry")
    target = sig_dict.get("target")
    if entry and target and entry > 0:
        profit_pct = abs(target - entry) / entry * 100
        if profit_pct < 2.0:
            return f"profit {profit_pct:.1f}% < 2.0% minimum", sig_dict

    # ── Pre-long-weekend confidence haircut (-5pp, non-blocking) ─────────────
    try:
        from services.market_calendar import get_upcoming_holidays, is_pre_long_weekend
        holidays = await get_upcoming_holidays()
        is_long_wknd, holiday_name = is_pre_long_weekend(holidays)
        if is_long_wknd:
            sig_dict = dict(sig_dict)
            sig_dict["confidence"] = round(max(35.0, sig_dict["confidence"] - 5.0), 1)
            sig_dict.setdefault("rationale", [])
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [{
                "src": "Risk Gate",
                "head": f"Pre-{holiday_name} Haircut (−5pp)",
                "body": (
                    f"Signal is 2 trading days before {holiday_name} (3-day weekend). "
                    "Lower liquidity, wider bid-ask spreads, and gap risk at open after "
                    "the holiday reduce expected return. Confidence reduced by 5pp."
                ),
                "sentiment": "neg",
                "meta": f"holiday={holiday_name} haircut=-5pp",
            }]
    except Exception:
        pass

    return None, sig_dict  # all gates passed
