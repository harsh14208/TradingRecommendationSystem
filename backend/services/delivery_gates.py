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

# ── §67 FOMC meeting dates (scheduled announcement days) ─────────────────────
_FOMC_DATES_2026 = frozenset(
    {
        "2026-01-28",
        "2026-03-18",
        "2026-04-29",
        "2026-06-17",
        "2026-07-29",
        "2026-09-16",
        "2026-10-28",
        "2026-12-16",
    }
)


def _days_to_nearest_fomc(today_str: str) -> int:
    from datetime import date as _date

    today = _date.fromisoformat(today_str)
    min_days = 999
    for ds in _FOMC_DATES_2026:
        d = _date.fromisoformat(ds)
        diff = abs((d - today).days)
        min_days = min(min_days, diff)
    return min_days


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Gate configuration ────────────────────────────────────────────────────────

# Empirical live data (543 resolved, Apr-May 2026) — alpha/beta decomposition:
#   Position: alpha +0.890%/trade, WR 56.6%  → keep flowing
#   Swing:    alpha −1.028%/trade, WR 41.2%  → only very-high-confidence setups
#   Intraday: alpha −0.321%/trade, WR 30.4%  → disabled
# Swing floor raised 62→65 (2026-05-26), then 65→70 (2026-05-30): persistent
# negative alpha (−1.028%/trade) — only near-ceiling setups worth trading.
STYLE_CONF_FLOORS: dict[str, float] = {
    "intraday": 999.0,  # DISABLED — alpha −0.321%/trade, WR 30.4% (May 2026 live data)
    "swing": 46.0,  # recalibrated 70→46 post phantom-win correction (2026-05-31).
    # Old 70% = top ~15% of phantom-inflated distribution (−1.028%/trade alpha, WR 41.2%).
    # On honest 40-50% confidence scale, 46% selects the upper half of the distribution.
    # Swing alpha was −1.028%/trade; only near-ceiling setups pass even at new scale.
    "position": 0.0,  # no additional floor — driven by global min_confidence (40%)
}

# Sectors with empirical PF < 0.40x blocked until per-sector models retrained.
# XLF 0.32x, XLP 0.35x, XLU insufficient data.
BLOCKED_SECTORS: frozenset[str] = frozenset({"XLF", "XLP", "XLU"})

# Tickers that don't exhibit 10-day price-level MR behavior:
#  - Semi equipment (LRCX, MRVL, AMAT, KLAC): continuation cycle, multi-quarter
#    IS: LRCX −7.20%, MRVL −6.65%; OOS: KLAC −4.36%, AMAT 0 trades
#  - XLF regional banks (STT, MTB): rate-cycle driven, not price-level MR
#    OOS v5: STT −4.75% (0% WR), MTB −4.16% (0% WR)
BLOCKED_TICKERS: frozenset[str] = frozenset(
    {
        "LRCX",
        "MRVL",
        "AMAT",
        "KLAC",  # semi equipment — continuation not MR (IS: LRCX −7.20%, MRVL −6.65%)
        "STT",
        "MTB",  # XLF regional banks — rate-cycle driven (OOS v5: both 0% WR)
        "APH",  # Amphenol — live data: N=4, 0% WR, −8.70% avg (2026-05-31)
        # Electronic connectors tied to industrial/auto cycles; MR thesis fails
    }
)

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

    # ── Ticker block (no 10-day MR behavior) ─────────────────────────────────
    if ticker in BLOCKED_TICKERS:
        _semi = {"LRCX", "MRVL", "AMAT", "KLAC"}
        _banks = {"STT", "MTB"}
        _connectors = {"APH"}
        if ticker in _semi:
            reason = "semi equipment — continuation not MR (LRCX −7.20%, KLAC −4.36% OOS)"
        elif ticker in _banks:
            reason = "XLF regional bank — rate-cycle driven, not price-level MR (OOS v5: 0% WR)"
        elif ticker in _connectors:
            reason = "electronic connectors — industrial/auto cycle, not price-level MR (live: N=4, 0% WR, −8.70%)"
        else:
            reason = "ticker-specific block (no MR edge confirmed)"
        return (f"{ticker} blocked — {reason}", sig_dict)

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

    # ── §54 VIX<15 suspension (ultra-low vol — MR setups statistically fail) ───
    # Backtest §54: VIX<15 regime shows mean-reversion entries cluster at bottom
    # of vol cycles; price continues rather than reverting. 23yr IS data confirms
    # suspending MR signals in ultra-calm regimes improves Sharpe (0.21→0.22).
    if action == "BUY":
        _vix_now = sig_dict.get("vix")
        if _vix_now is not None and _vix_now < 15.0:
            return f"VIX={_vix_now:.1f} < 15 — MR entry suspended in ultra-low vol regime (§54)", sig_dict

    # ── §55 Cross-asset macro hard block (3/3 headwinds) ─────────────────────
    # Backtest §55: 3/3 headwinds (TLT+UUP+XLE stress) → +0.03 Sharpe when blocked.
    # macro.py applies −10 soft score reduction; this adds a hard block for
    # extreme confluence. 5 trades/23yr blocked, all were losers.
    if action == "BUY":
        _ca = sig_dict.get("crossAssetHeadwinds")
        if _ca is not None and _ca >= 3:
            return "3/3 cross-asset macro headwinds (TLT+UUP+XLE) — hard block (§55)", sig_dict

    # ── Pre-earnings blackout (≤2 trading days) ───────────────────────────────
    dte = sig_dict.get("daysToEarnings")
    if dte is not None and 0 < dte <= 2:
        return f"{dte}d to earnings — pre-earnings hard blackout", sig_dict

    # ── Ex-dividend blackout (0–2 days to ex-div, BUY only) ───────────────────
    # Stock drops by dividend amount on ex-div date — structural, not a panic dip.
    # Only gate BUY; HOLD/SELL are unaffected.
    if action == "BUY":
        _exdiv = sig_dict.get("daysToExDiv")
        if _exdiv is not None and 0 <= _exdiv <= 2:
            return (
                f"Ex-dividend in {_exdiv}d — price drop structural not panic, MR entry blocked",
                sig_dict,
            )

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

    # ── §57 Thursday signal confidence haircut (−3pp, non-blocking) ──────────
    # Thursday BUY signals fill at Friday open — pre-weekend de-risking by
    # institutions, wider bid-ask spreads, and gap risk on Monday opening all
    # reduce fill quality. Live data §11a (437 signals): Thursday WR 56.2% vs
    # Tuesday 70.1% (14pp gap). Applied only to BUY signals; waived if confidence
    # is already high (≥58pp) since those represent exceptional setups.
    try:
        _now_utc = datetime.now(timezone.utc)
        if action == "BUY" and _now_utc.weekday() == 3:  # Thursday = 3
            _conf_before = sig_dict.get("confidence", 0)
            if _conf_before < 58.0:
                sig_dict = dict(sig_dict)
                sig_dict["confidence"] = round(max(35.0, _conf_before - 3.0), 1)
                sig_dict.setdefault("rationale", [])
                sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                    {
                        "src": "Risk Gate",
                        "head": "Thursday Fill Haircut (−3pp)",
                        "body": (
                            "Thursday signals fill at Friday open — pre-weekend institutional "
                            "de-risking and wider spreads reduce fill quality. Live data shows "
                            "14pp WR gap vs Tuesday (56.2% vs 70.1% across 437 signals). "
                            "Confidence reduced by 3pp."
                        ),
                        "sentiment": "neg",
                        "meta": "dow=thursday haircut=-3pp §57",
                    }
                ]
    except Exception:
        pass

    # ── §67 FOMC Proximity caution (≤1 day) ──────────────────────────────────
    if action == "BUY":
        _today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _fomc_dist = _days_to_nearest_fomc(_today_str)
        if _fomc_dist == 0:
            return "FOMC decision day — rate announcement gap risk, MR entry blocked", sig_dict
        elif _fomc_dist == 1:
            sig_dict = dict(sig_dict)
            sig_dict["confidence"] = round(max(35.0, sig_dict.get("confidence", 0) - 4.0), 1)
            sig_dict.setdefault("rationale", [])
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                {
                    "src": "Risk Gate",
                    "head": "FOMC Tomorrow — Rate Decision Uncertainty (−4pp)",
                    "body": (
                        "Tomorrow is a scheduled FOMC rate decision. Pre-decision gap risk and "
                        "intraday volatility reduce fill quality and MR hold reliability. "
                        "Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "fomc_dist=1d haircut=-4pp (§67)",
                }
            ]

    # ── §78 Sep/Oct seasonality — worst calendar months, raise entry bar ─────
    _month = datetime.now(timezone.utc).month
    _conf = sig_dict.get("confidence", 0)
    if action == "BUY" and _month == 9 and _conf < 62:
        return (
            f"September seasonality gate — worst calendar month, confidence {_conf:.0f}% below 62% threshold",
            sig_dict,
        )
    if action == "BUY" and _month == 10 and _conf < 60:
        return (
            f"October seasonality gate — elevated whipsaw risk, confidence {_conf:.0f}% below 60% threshold",
            sig_dict,
        )

    return None, sig_dict  # all gates passed
