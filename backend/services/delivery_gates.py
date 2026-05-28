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
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

log = logging.getLogger("scanner")


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Gate configuration ────────────────────────────────────────────────────────

# Empirical live data (543 resolved, Apr-May 2026) — alpha/beta decomposition:
#   Position: alpha +0.890%/trade, WR 56.6%  → keep flowing
#   Swing:    alpha −1.028%/trade, WR 41.2%  → only very-high-confidence setups
#   Intraday: alpha −0.321%/trade, WR 30.4%  → disabled
# Swing floor raised 62→65 (2026-05-26): live alpha −1.028% confirms only
# near-ceiling (65%+) swing setups carry positive expected value.
STYLE_CONF_FLOORS: dict[str, float] = {
    "intraday": 999.0,  # DISABLED — alpha −0.321%/trade, WR 30.4% (May 2026 live data)
    "swing": 65.0,  # raised 62→65 — alpha −1.028%/trade; only ≥65% setups pass
    "position": 0.0,  # no additional floor — driven by global min_confidence (57%)
}

# Sectors with empirical PF < 0.40x blocked until per-sector models retrained.
# XLF 0.32x, XLP 0.35x, XLU insufficient data.
BLOCKED_SECTORS: frozenset[str] = frozenset({"XLF", "XLP", "XLU"})

# Same-underlying aliases: if GOOGL signal fires, it counts as a GOOG position
# (and vice versa) — both are Alphabet equity, different share classes only.
TICKER_ALIASES: dict[str, str] = {
    "GOOGL": "GOOG",
    "GOOG": "GOOGL",
}


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
    conf = sig_dict.get("confidence", 0)

    # ── Action guard ─────────────────────────────────────────────────────────
    if action not in ("BUY", "SELL"):
        return f"action={action} not BUY/SELL", sig_dict

    # ── Ticker-adaptive confidence floor (checked before global floor) ─────────
    # High-win tickers (≥75% historical WR) get a relaxed 52% floor instead of
    # the global min_confidence, so quality tickers aren't killed by a high global
    # setting. Low-win tickers (<45% WR) must clear a stricter 68% bar.
    _effective_conf_floor = settings.min_confidence
    try:
        from database import AsyncSessionLocal
        from models import AppSettings

        async with AsyncSessionLocal() as _adb:
            _srow = (await _adb.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
        app_data = (_srow.data or {}) if _srow else {}
        ticker_wrs = app_data.get("adaptive_weights", {}).get("ticker_win_rates", {})
        twr = ticker_wrs.get(ticker)
        if twr is not None:
            if twr < 0.45:
                _effective_conf_floor = max(_effective_conf_floor, 68.0)
            elif twr >= 0.75:
                _effective_conf_floor = min(_effective_conf_floor, 52.0)
    except Exception:
        pass

    # ── Global confidence floor (with ticker-adaptive override) ──────────────
    if conf < _effective_conf_floor:
        return (
            f"conf {conf:.0f}% < global floor {_effective_conf_floor:.0f}%",
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
    # Also check ticker itself: sector ETFs (XLF, XLP, XLU) have sector_etf=None
    # because they ARE the sector — the column isn't self-referential.
    ticker_as_sector = sig_dict.get("ticker", "")
    if (sector and sector in BLOCKED_SECTORS) or (ticker_as_sector in BLOCKED_SECTORS):
        _blocked_key = sector if (sector and sector in BLOCKED_SECTORS) else ticker_as_sector
        return (
            f"sector {_blocked_key} blocked (low PF) — awaiting retraining",
            sig_dict,
        )

    # ── Pre-earnings blackout (≤2 trading days) ───────────────────────────────
    dte = sig_dict.get("daysToEarnings")
    if dte is not None and 0 < dte <= 2:
        return f"{dte}d to earnings — pre-earnings hard blackout", sig_dict

    # ── Sector concentration limit (max 2 BUY per sector per 24h) ────────────
    if sector and action == "BUY":
        from models import Signal

        cutoff = _utcnow_naive() - timedelta(hours=24)
        count = (
            await db.execute(
                select(func.count())
                .select_from(Signal)
                .where(Signal.sector_etf == sector)
                .where(Signal.action == "BUY")
                .where(Signal.is_sent == True)
                .where(Signal.sent_at >= cutoff)
            )
        ).scalar_one()
        if count >= 2:
            return f"sector {sector} already has {count} BUY sends in 24h (max 2)", sig_dict

    # ── Same-underlying deduplication (GOOG/GOOGL alias gate) ────────────────
    # Both share classes map to the same Alphabet equity position. If either
    # alias was sent as BUY in the last 24h, block the other to prevent
    # unintended double-sizing on a single underlying.
    alias = TICKER_ALIASES.get(ticker)
    if alias and action == "BUY":
        from models import Signal

        cutoff = _utcnow_naive() - timedelta(hours=24)
        alias_count = (
            await db.execute(
                select(func.count())
                .select_from(Signal)
                .where(Signal.ticker == alias)
                .where(Signal.action == "BUY")
                .where(Signal.is_sent == True)
                .where(Signal.sent_at >= cutoff)
            )
        ).scalar_one()
        if alias_count > 0:
            return (
                f"{ticker} blocked — alias {alias} already sent as BUY within 24h (same underlying)",
                sig_dict,
            )

    # ── Source independence gate ──────────────────────────────────────────────
    sources_set = set(sig_dict.get("sources") or [])
    non_ta = sources_set - {
        "Technical",
        "Technicals",
        "Risk Gate",
        "Backtest",
        "Cross-Sectional",
        "Orthogonalization",
        "Signal Cluster",
    }
    # Swing requires same independent corroboration as position (§33 live alpha:
    # swing −1.028%/trade at 65% floor; single non-TA source insufficient to
    # distinguish genuine MR setups from momentum-continuation pullbacks).
    min_non_ta = 2 if style in ("position", "swing") else 1
    if len(non_ta) < min_non_ta:
        return (
            f"only {len(non_ta)} non-TA sources for {style} (need {min_non_ta})",
            sig_dict,
        )

    # ── Minimum profit filter ─────────────────────────────────────────────────
    entry = sig_dict.get("entry")
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
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                {
                    "src": "Risk Gate",
                    "head": f"Pre-{holiday_name} Haircut (−5pp)",
                    "body": (
                        f"Signal is 2 trading days before {holiday_name} (3-day weekend). "
                        "Lower liquidity, wider bid-ask spreads, and gap risk at open after "
                        "the holiday reduce expected return. Confidence reduced by 5pp."
                    ),
                    "sentiment": "neg",
                    "meta": f"holiday={holiday_name} haircut=-5pp",
                }
            ]
    except Exception:
        pass

    return None, sig_dict  # all gates passed
