"""Programmatic options VRP/recommendation engine wrapper.

This module exposes a clean, async-loop-safe API around the validated VRP logic in
``scripts/orats_opportunity_model`` and ``scripts/orats_recommendation_engine``.
It is intended to be called from ``services/scanner.py`` after the regular stock
scan, so the option layer reuses the live directional view and earnings data the
scanner already fetched.

The wrapper is **synchronous** because the underlying XGB/scikit models and
pandas transforms are CPU-bound.  Callers running inside an asyncio event loop
should invoke it via ``asyncio.to_thread`` (e.g. the scanner).

Three execution modes are supported per user (see ``User.options_mode``):
  * signal  — generate/store option signals, send alerts, no broker call
  * paper   — simulate fills and track P&L in ``broker_orders``
  * live    — place real option orders through the configured broker client

Signal payloads are additive: a ``Signal`` row with an ``option_strategy`` is
still a normal signal (action BUY/SELL for gating/delivery) but carries the
option plan in dedicated nullable columns.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Pure functions from the validated recommendation engine.
from scripts.orats_recommendation_engine import (  # noqa: E402
    _INDEX_ETFS,
    _decide,
    _trade_plan,
    build_book,
)
from scripts.orats_opportunity_model import get_vol_view  # noqa: E402

log = logging.getLogger("signal.options_engine")

# Avoid a hard dependency if the chain resolver is not imported in this process.
try:
    from services.options_chain_resolver import (  # noqa: F401
        OptionContract,
        select_contract,
        target_delta_for_leg,
    )
except Exception:  # pragma: no cover - defensive for isolated workers
    OptionContract = None  # type: ignore[misc,assignment]
    select_contract = None  # type: ignore[misc,assignment]
    target_delta_for_leg = None  # type: ignore[misc,assignment]


# Default risk settings mirror the plan's signal-only defaults.
DEFAULT_CAPITAL = 50_000.0
DEFAULT_RISK_PER_TRADE = 0.01
DEFAULT_MAX_BOOK_RISK = 0.10
DEFAULT_MAX_POSITIONS = 15
DEFAULT_MAX_IV_SELL = 0.80
DEFAULT_MIN_OPT_VOLUME = 500.0
DEFAULT_HORIZON = 2

# Option strategies that involve actual option contracts and should be persisted
# as option signals.  BUY_STOCK is deliberately excluded — the stock scanner
# already owns directional stock recommendations.
_OPTION_ACTIONS = {
    "SELL_CASH_SEC_PUT",
    "SELL_STRANGLE",
    "SELL_DEFINED_RISK",
    "LONG_STRADDLE",
}

# Leveraged/inverse ETF patterns we never sell premium on.  These names can
# gap 5-10% overnight and the Massive IV surface is frequently dislocated.
_LEVERAGE_PATTERNS = (
    "3X",
    "2X",
    "ULTRA",
    "INVERSE",
    "SHORT",
    "BEAR",
    "BULL",
    "SQQQ",
    "TQQQ",
    "UVXY",
    "VXX",
    "SOXL",
    "SOXS",
    "SPXL",
    "SPXS",
    "LABU",
    "LABD",
    "FAS",
    "FAZ",
    "TECL",
    "TECS",
)


def _is_leveraged(ticker: str) -> bool:
    return ticker.upper() in _LEVERAGE_PATTERNS or any(p in ticker.upper() for p in _LEVERAGE_PATTERNS)


def _nearest_monthly_expiry(as_of: date, min_days: int = 14) -> date:
    """Return the third Friday of a month at least ``min_days`` after as_of.

    This is a conservative placeholder for signal-only payloads.  Live execution
    will resolve the exact expiry/strike from the broker's option chain snapshot.
    """
    d = as_of + timedelta(days=min_days)
    # Move to first of the target month (or keep current if already past min_days
    # but before expiry).
    d = date(d.year, d.month, 1)
    while True:
        # Find third Friday.
        weekday_friday = 4
        first_day_weekday = d.weekday()
        days_to_friday = (weekday_friday - first_day_weekday) % 7
        third_friday = d + timedelta(days=days_to_friday + 14)
        if third_friday >= as_of + timedelta(days=min_days):
            return third_friday
        # Advance to next month.
        if d.month == 12:
            d = date(d.year + 1, 1, 1)
        else:
            d = date(d.year, d.month + 1, 1)


def _build_option_legs(
    row: pd.Series,
    expiry: date,
    chain: list[OptionContract] | None = None,
) -> list[dict[str, Any]]:
    """Construct an option-leg plan from a recommendation row.

    When ``chain`` is supplied, the function selects the exact expiry/strike from
    real Polygon snapshot contracts and applies liquidity/spread filters.  Without
    a chain it falls back to the original nearest-monthly placeholder strikes.
    """
    action = row["action"]
    px = float(row["stk_px"])
    impl = float(row["impl_move"])
    qty = max(1, int(round(row["units"])))
    ticker = row["ticker"]

    def _placeholder_leg(option_type: str, strike: float, position: str) -> dict[str, Any]:
        side_letter = "C" if option_type == "call" else "P"
        sym = f"O:{ticker}{expiry.strftime('%y%m%d')}{side_letter}{int(round(float(strike) * 1000)):08d}"
        return {
            "option_type": option_type,
            "side": "buy" if position == "long" else "sell",
            "position": position,
            "option_symbol": sym,
            "quantity": int(qty),
            "strike": round(float(strike), 2),
            "expiry": expiry.isoformat(),
            "premium": round(float(row["exp_gain"]) / int(qty), 4) if qty else 0.0,
            "midpoint": None,
            "bid": None,
            "ask": None,
            "resolved": False,
        }

    def _resolve_leg(option_type: str, strike: float, position: str) -> dict[str, Any] | None:
        if not chain or select_contract is None:
            return None
        target_delta = target_delta_for_leg(action, option_type, position)
        contract = select_contract(
            chain,
            ctype=option_type,
            target_expiry=expiry,
            target_strike=strike,
            target_delta=target_delta,
        )
        if contract is None:
            return None
        return {
            "option_type": option_type,
            "side": "buy" if position == "long" else "sell",
            "position": position,
            "option_symbol": contract.option_symbol,
            "quantity": int(qty),
            "strike": contract.strike,
            "expiry": contract.expiry.isoformat(),
            "premium": round(contract.midpoint, 4),
            "midpoint": round(contract.midpoint, 4),
            "bid": round(contract.bid, 4),
            "ask": round(contract.ask, 4),
            "resolved": True,
        }

    def _leg(option_type: str, strike: float, position: str) -> dict[str, Any]:
        return _resolve_leg(option_type, strike, position) or _placeholder_leg(option_type, strike, position)

    if action == "SELL_CASH_SEC_PUT":
        strike = px * (1.0 - impl * 0.5)
        return [_leg("put", strike, "short")]

    if action in ("SELL_STRANGLE", "SELL_DEFINED_RISK"):
        call_strike = px * (1.0 + impl)
        put_strike = px * (1.0 - impl)
        legs = [_leg("call", call_strike, "short"), _leg("put", put_strike, "short")]
        if action == "SELL_DEFINED_RISK":
            long_call_strike = call_strike * 1.05
            long_put_strike = put_strike * 0.95
            legs.extend(
                [
                    _leg("call", long_call_strike, "long"),
                    _leg("put", long_put_strike, "long"),
                ]
            )
        return legs

    if action == "LONG_STRADDLE":
        strike = px
        return [_leg("call", strike, "long"), _leg("put", strike, "long")]

    return []


def _backfill_earnings(df: pd.DataFrame, horizon: int, fetch: bool) -> pd.DataFrame:
    """Fill missing days_to_earnings for candidate names using yfinance."""
    need = df[(df["days_to_earnings"].isna()) & ((df["richness_pct"] >= 0.80) | (df["dir_action"] == "BUY"))][
        "ticker"
    ].tolist()
    if not need or not fetch:
        return df
    log.info("Backfilling earnings dates for %d option candidates…", len(need))
    try:
        from scripts.orats_recommendation_engine import _earnings_for

        dte_map = asyncio.run(_earnings_for(need))
    except Exception:
        log.exception("Failed to backfill earnings for option candidates")
        return df
    df["days_to_earnings"] = df.apply(
        lambda r: dte_map.get(r["ticker"]) if pd.isna(r["days_to_earnings"]) else r["days_to_earnings"],
        axis=1,
    )
    return df


def score_options_universe(
    universe: str = "companies",
    as_of: date | None = None,
    capital: float = DEFAULT_CAPITAL,
    risk_per_trade: float = DEFAULT_RISK_PER_TRADE,
    max_book_risk: float = DEFAULT_MAX_BOOK_RISK,
    max_positions: int = DEFAULT_MAX_POSITIONS,
    max_iv_sell: float = DEFAULT_MAX_IV_SELL,
    min_opt_volume: float = DEFAULT_MIN_OPT_VOLUME,
    horizon: int = DEFAULT_HORIZON,
    model_name: str = "xgb",
    direction_df: pd.DataFrame | None = None,
    earnings_map: dict[str, int | None] | None = None,
    fetch_missing_earnings: bool = True,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Score one options universe and return (summary, all_recs, risk_capped_book).

    Parameters
    ----------
    universe:
        ``companies``, ``etf``, or ``index``.  ``index`` trains on the ETF universe
        then filters to broad-market/sector index ETFs and forces defined-risk.
    as_of:
        Date for which recommendations are desired.  Currently this must match the
        latest date available in ``orats_daily_features``; the function will raise
        if a newer panel is required.
    capital, risk_per_trade, max_book_risk, max_positions, max_iv_sell:
        Risk/sizing parameters (see plan defaults).
    min_opt_volume:
        Minimum total option contracts traded yesterday for a name to be scored.
    horizon:
        Trading-day forecast horizon (default 2, matching the validated VRP edge).
    model_name:
        ``xgb`` (default) or ``ridge``.
    direction_df:
        Optional DataFrame with columns ``ticker, dir_action, dir_confidence,
        dir_score, dir_entry, dir_stop, dir_target, days_to_earnings,
        next_earnings_date``.  If omitted, option recommendations will be purely
        volatility-based (no directional fusion).
    earnings_map:
        Optional ``{ticker: days_to_earnings}`` override.  Non-candidate names can
        map to ``None``.  Takes precedence over ``direction_df`` values.
    fetch_missing_earnings:
        If True and running in a context with an event loop available, backfill
        missing earnings via yfinance for rich names and directional BUYs.

    Returns
    -------
    summary:
        Dict from ``get_vol_view`` plus ``universe`` and ``as_of``.
    all_recs:
        DataFrame of every scored name with ``action``, ``rationale``, trade-plan
        columns, and ``option_legs``.
    book:
        Risk-capped subset chosen by ``build_book``.
    """
    if universe not in {"companies", "etf", "index"}:
        raise ValueError(f"universe must be companies|etf|index, got {universe}")

    # Index mode trains on the full ETF universe for statistical depth, then filters.
    vol_universe = "etf" if universe == "index" else universe

    log.info("Scoring options universe=%s (vol_universe=%s, horizon=%d)", universe, vol_universe, horizon)
    summary, vol = get_vol_view(
        universe=vol_universe,
        horizon=horizon,
        model_name=model_name,
        min_opt_volume=min_opt_volume,
    )
    latest = pd.Timestamp(summary["latest_date"]).date()
    if as_of is None:
        as_of = latest
    elif as_of < latest:
        raise ValueError(f"Requested as_of={as_of} is older than latest panel date={latest}")

    summary["universe"] = universe
    summary["as_of"] = as_of.isoformat()

    if universe == "index":
        vol = vol[vol["ticker"].isin(_INDEX_ETFS)].reset_index(drop=True)
        log.info("Index mode: filtered to %d broad-market/sector index ETFs", len(vol))

    # ── Fuse with directional view ──
    if direction_df is not None and not direction_df.empty:
        keep_cols = [
            "ticker",
            "dir_action",
            "dir_confidence",
            "dir_score",
            "dir_entry",
            "dir_stop",
            "dir_target",
            "days_to_earnings",
            "next_earnings_date",
        ]
        direction_df = direction_df[[c for c in keep_cols if c in direction_df.columns]].copy()
        df = vol.merge(direction_df, on="ticker", how="left")
    else:
        df = vol.assign(
            dir_action=None,
            dir_confidence=None,
            dir_score=None,
            dir_entry=None,
            dir_stop=None,
            dir_target=None,
            days_to_earnings=None,
            next_earnings_date=None,
        )

    # Apply earnings override if provided.
    if earnings_map:
        df["days_to_earnings"] = df.apply(
            lambda r: earnings_map.get(r["ticker"], r["days_to_earnings"]),
            axis=1,
        )

    # Backfill missing earnings only for candidates where it affects the decision.
    df = _backfill_earnings(df, horizon, fetch_missing_earnings)

    # ── Decide action and plan trade ──
    actions = df.apply(lambda r: _decide(r, horizon), axis=1)
    df["action"] = [a for a, _ in actions]
    df["rationale"] = [w for _, w in actions]

    if universe == "index":
        m = df["action"] == "SELL_STRANGLE"
        df.loc[m, "action"] = "SELL_DEFINED_RISK"
        df.loc[m, "rationale"] = df.loc[m, "rationale"].str.replace(
            "→ harvest VRP",
            "→ sell DEFINED-RISK premium (iron condor / put spread), never naked — index tail is undiversifiable",
            regex=False,
        )

    # Additional safety filters beyond what the scripts already do.
    # 1) Never sell premium on leveraged/inverse names (their IV is often stale/dislocated).
    sell_mask = df["action"].str.startswith("SELL", na=False)
    lev_mask = df["ticker"].apply(_is_leveraged)
    df.loc[sell_mask & lev_mask, "action"] = "NO_ACTION"
    df.loc[sell_mask & lev_mask, "rationale"] = "Leveraged/inverse ETF excluded from premium-selling"

    ratio_q = summary.get("ratio_q", [])
    plan = df.apply(lambda r: _trade_plan(r, ratio_q, capital, risk_per_trade), axis=1)
    plan_df = pd.DataFrame(list(plan), index=df.index)
    df = pd.concat([df, plan_df], axis=1)

    # Build tentative option legs for signal payloads.
    expiry = _nearest_monthly_expiry(as_of, min_days=max(horizon + 5, 14))
    df["option_legs"] = df.apply(
        lambda r: _build_option_legs(r, expiry) if r["action"] in _OPTION_ACTIONS else [], axis=1
    )

    # ── Risk-capped book ──
    book = build_book(df, capital, max_book_risk, max_positions, max_iv_sell)

    # Force defined-risk sizing cap for index mode (max loss already bounded by spread).
    if universe == "index" and not book.empty:
        book = book[book["action"] != "SELL_STRANGLE"].copy()

    log.info(
        "Options scoring done: %d scored, %d actionable, %d in risk-capped book",
        len(df),
        df["action"].isin(_OPTION_ACTIONS).sum(),
        len(book),
    )
    return summary, df, book


def book_to_signal_dicts(book: pd.DataFrame, summary: dict) -> list[dict[str, Any]]:
    """Convert the risk-capped book into signal payloads for ``_persist_scan_signals``.

    Each payload contains the standard signal keys the delivery gates expect, plus
    the option-specific keys that will be persisted in the ``Signal`` row.
    """
    if book.empty:
        return []

    signals: list[dict[str, Any]] = []
    latest = summary.get("latest_date", datetime.utcnow().date().isoformat())
    for _, r in book.iterrows():
        action = "BUY" if r["action"] in {"BUY_STOCK", "LONG_STRADDLE"} else "SELL"
        # Confidence is a blend of win probability and richness rank.
        win = r.get("win_prob") if pd.notna(r.get("win_prob")) else 0.5
        richness = r.get("richness") if pd.notna(r.get("richness")) else 1.0
        confidence = min(95.0, max(50.0, round((win * 50.0 + min(richness, 2.0) / 2.0 * 50.0), 1)))

        sig = {
            "ticker": r["ticker"],
            "company": None,
            "action": action,
            "confidence": confidence,
            "raw_confidence": confidence,
            "confidence_warning": False,
            "price": float(r["stk_px"]),
            "change": 0.0,
            "changePct": 0.0,
            "entry": float(r["stk_px"]),
            "stop": None,
            "target": None,
            "rr": None,
            "headline": f"{r['action']}: {r['ticker']} ({r['rationale']})",
            "sentiment": 0,
            "style": "options_vrp",
            "sources": ["options_engine"],
            "rationale": [r["rationale"]],
            "plain_english": {
                "summary": r["rationale"],
                "tf_short": f"Options VRP scan for {latest}",
                "top_reasons": [f"implied {r['impl_move'] * 100:.1f}% vs forecast {r['forecast_move'] * 100:.1f}%"],
            },
            "session": "afterhours",
            "daysToEarnings": int(r["days_to_earnings"]) if pd.notna(r.get("days_to_earnings")) else None,
            "nextEarningsDate": r.get("next_earnings_date"),
            "sectorEtf": None,
            "rsVsSector": None,
            # Option-specific payload (mirrors the Signal model columns).
            "option_strategy": r["action"],
            "option_legs": (_legs := list(r.get("option_legs", []))),
            "option_liquidity_ok": all(leg.get("resolved") for leg in _legs) if _legs else False,
            "option_underlying_action": r.get("dir_action"),
            "option_richness": float(r["richness"]) if pd.notna(r.get("richness")) else None,
            "option_impl_move": float(r["impl_move"]) if pd.notna(r.get("impl_move")) else None,
            "option_forecast_move": float(r["forecast_move"]) if pd.notna(r.get("forecast_move")) else None,
            "option_exp_gain": float(r["exp_gain"]) if pd.notna(r.get("exp_gain")) else None,
            "option_max_loss": float(r["max_loss"]) if pd.notna(r.get("max_loss")) else None,
            "option_days_to_earnings": int(r["days_to_earnings"]) if pd.notna(r.get("days_to_earnings")) else None,
        }
        signals.append(sig)
    return signals
