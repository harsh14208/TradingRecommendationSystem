"""Unit tests for the options VRP engine wrapper and scanner hook."""

from __future__ import annotations

import pandas as pd
import pytest

from services.options_engine import _build_option_legs, _nearest_monthly_expiry, book_to_signal_dicts
from services.options_scanner import _build_direction_df, _persist_option_signals


def test_build_direction_df_maps_stock_signals() -> None:
    stock = [
        {
            "ticker": "AAPL",
            "action": "BUY",
            "confidence": 78.0,
            "raw_score": 0.8,
            "entry": 170.0,
            "stop": 165.0,
            "target": 180.0,
            "daysToEarnings": 12,
            "nextEarningsDate": "2026-07-15",
        },
        {"ticker": "TSLA", "action": "HOLD"},
    ]
    df = _build_direction_df(stock)
    assert len(df) == 1
    assert df.iloc[0]["ticker"] == "AAPL"
    assert df.iloc[0]["dir_action"] == "BUY"
    assert df.iloc[0]["days_to_earnings"] == 12


def test_build_option_legs_long_straddle() -> None:
    row = pd.Series(
        {
            "ticker": "AAPL",
            "stk_px": 170.0,
            "action": "LONG_STRADDLE",
            "impl_move": 0.015,
            "exp_gain": 5.0,
            "units": 2.0,
        }
    )
    expiry = _nearest_monthly_expiry(pd.Timestamp("2026-06-18").date())
    legs = _build_option_legs(row, expiry)
    assert len(legs) == 2
    assert legs[0]["option_type"] == "call"
    assert legs[1]["option_type"] == "put"
    assert legs[0]["side"] == "buy"
    assert legs[0]["quantity"] == 2
    assert legs[0]["strike"] == 170.0
    assert legs[0]["position"] == "long"


def test_build_option_legs_cash_secured_put() -> None:
    row = pd.Series(
        {
            "ticker": "AAPL",
            "stk_px": 170.0,
            "action": "SELL_CASH_SEC_PUT",
            "impl_move": 0.02,
            "exp_gain": 3.0,
            "units": 1.0,
        }
    )
    expiry = _nearest_monthly_expiry(pd.Timestamp("2026-06-18").date())
    legs = _build_option_legs(row, expiry)
    assert len(legs) == 1
    assert legs[0]["option_type"] == "put"
    assert legs[0]["side"] == "sell"
    assert legs[0]["position"] == "short"
    assert legs[0]["strike"] < 170.0


def test_book_to_signal_dicts() -> None:
    expiry = _nearest_monthly_expiry(pd.Timestamp("2026-06-18").date())
    legs = [
        {
            "option_type": "call",
            "side": "buy",
            "option_symbol": "O:AAPL260717C00170000",
            "quantity": 1,
            "strike": 170.0,
            "expiry": expiry.isoformat(),
            "premium": 5.0,
            "position": "long",
        }
    ]
    book = pd.DataFrame(
        [
            {
                "ticker": "AAPL",
                "action": "LONG_STRADDLE",
                "stk_px": 170.0,
                "richness": 0.85,
                "impl_move": 0.015,
                "forecast_move": 0.018,
                "exp_gain": 5.0,
                "max_loss": 8.0,
                "win_prob": 0.55,
                "days_to_earnings": None,
                "next_earnings_date": None,
                "dir_action": None,
                "option_legs": legs,
                "rationale": "cheap",
            }
        ]
    )
    summary = {"latest_date": "2026-06-18"}
    sigs = book_to_signal_dicts(book, summary)
    assert len(sigs) == 1
    sig = sigs[0]
    assert sig["action"] == "BUY"
    assert sig["option_strategy"] == "LONG_STRADDLE"
    assert sig["option_legs"] == legs
    assert sig["option_richness"] == pytest.approx(0.85)
    assert sig["style"] == "options_vrp"


@pytest.mark.asyncio
async def test_persist_option_signals_dedupes_by_ticker() -> None:
    """Only one active option signal should exist per ticker after a scan."""
    from datetime import datetime, timezone

    from database import AsyncSessionLocal, engine
    from models import Signal
    from sqlalchemy import select

    # Ensure a fresh schema for this test.
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Signal.metadata.create_all(sync_conn))

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Pre-existing active option signal for AAPL.
    async with AsyncSessionLocal() as db:
        db.add(
            Signal(
                ticker="AAPL",
                action="SELL",
                confidence=60.0,
                price=170.0,
                headline="old",
                option_strategy="SELL_STRANGLE",
                is_active=True,
                created_at=today_start,
                expires_at=today_start,
            )
        )
        await db.commit()

    # Two signals for AAPL (different strategies) — only the first should persist.
    new_sigs = [
        {
            "ticker": "AAPL",
            "action": "SELL",
            "confidence": 70.0,
            "price": 171.0,
            "headline": "new straddle",
            "option_strategy": "LONG_STRADDLE",
        },
        {
            "ticker": "AAPL",
            "action": "SELL",
            "confidence": 65.0,
            "price": 171.0,
            "headline": "new csp",
            "option_strategy": "SELL_CASH_SEC_PUT",
        },
        {
            "ticker": "TSLA",
            "action": "SELL",
            "confidence": 60.0,
            "price": 250.0,
            "headline": "tesla",
            "option_strategy": "SELL_CASH_SEC_PUT",
        },
    ]

    await _persist_option_signals(new_sigs, today_start)

    async with AsyncSessionLocal() as db:
        rows = (
            (await db.execute(select(Signal).where(Signal.ticker == "AAPL").order_by(Signal.created_at)))
            .scalars()
            .all()
        )

    # Old signal deactivated; exactly one new active signal remains for AAPL.
    assert len([r for r in rows if r.is_active]) == 1
    active = [r for r in rows if r.is_active][0]
    assert active.option_strategy == "LONG_STRADDLE"
    assert active.headline == "new straddle"
    assert len([r for r in rows if not r.is_active]) == 1

    async with AsyncSessionLocal() as db:
        tsla_rows = (await db.execute(select(Signal).where(Signal.ticker == "TSLA"))).scalars().all()
    assert len([r for r in tsla_rows if r.is_active]) == 1

    # Cleanup.
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Signal.metadata.drop_all(sync_conn))
