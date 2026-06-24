"""Tests for services/options_paper.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import BrokerOrder
from services.brokers.options_broker import OptionLeg, OptionOrder
from services.options_chain_resolver import OptionContract
from services.options_paper import close_paper_position, resolve_paper_pnl, simulate_fill


def _contract(mid: float, bid: float | None = None, ask: float | None = None) -> OptionContract:
    bid = bid if bid is not None else mid - 0.05
    ask = ask if ask is not None else mid + 0.05
    return OptionContract(
        option_symbol="O:AAPL260717C00170000",
        underlying="AAPL",
        ctype="call",
        strike=170.0,
        expiry=__import__("datetime").date(2026, 7, 17),
        bid=bid,
        ask=ask,
        midpoint=mid,
        spread=ask - bid,
        spread_pct=(ask - bid) / mid,
        volume=100,
        open_interest=500,
        delta=0.50,
        iv=0.30,
    )


async def _in_memory_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session(), engine


@pytest.mark.asyncio
async def test_simulate_fill_records_broker_order() -> None:
    order = OptionOrder(
        underlying="AAPL",
        strategy="LONG_STRADDLE",
        legs=[
            OptionLeg(
                side="buy",
                position="long",
                option_symbol="O:AAPL260717C00170000",
                quantity=1,
                strike=170.0,
                expiry="2026-07-17",
            )
        ],
        max_loss=1000.0,
        expected_gain=50.0,
    )
    signal = {"entry": 170.0, "price": 170.0}

    session, engine = await _in_memory_session()
    async with session:
        with patch(
            "services.options_paper.fetch_contract_snapshot", new_callable=AsyncMock, return_value=_contract(2.0)
        ):
            order_record = await simulate_fill(order, signal, session)

        assert order_record.broker == "paper_options"
        assert order_record.status == "filled"
        assert order_record.symbol == "AAPL"
        assert order_record.side == "buy"
        assert order_record.filled_qty == 1
        assert order_record.option_legs is not None
        assert order_record.option_legs[0]["entry_fill"] == 2.05  # ask for long buy
        assert order_record.realized_pnl is not None
    await engine.dispose()


@pytest.mark.asyncio
async def test_submit_paper_option_order_submits_and_dedupes() -> None:
    from sqlalchemy import select

    from services.options_paper import submit_paper_option_order

    sig = {
        "ticker": "AAPL",
        "option_strategy": "SELL_STRANGLE",
        "price": 170.0,
        "entry": 170.0,
        "option_max_loss": 150.0,
        "option_exp_gain": 10.0,
        "option_legs": [
            {
                "option_symbol": "O:AAPL260717C00180000",
                "position": "short",
                "side": "sell",
                "quantity": 1,
                "strike": 180.0,
                "expiry": "2026-07-17",
            },
            {
                "option_symbol": "O:AAPL260717P00160000",
                "position": "short",
                "side": "sell",
                "quantity": 1,
                "strike": 160.0,
                "expiry": "2026-07-17",
            },
        ],
    }
    fake_broker = type(
        "FB",
        (),
        {"place_option_order": AsyncMock(return_value={"status": "accepted", "alpaca_order_id": "abc123"})},
    )()
    session, engine = await _in_memory_session()
    async with session:
        with patch("services.brokers.alpaca_options.AlpacaOptionsBroker", return_value=fake_broker):
            first = await submit_paper_option_order(sig, 11, session, "k", "s")
            assert first is not None
            assert first.broker == "alpaca_options"
            assert first.account_type == "paper"
            assert first.symbol == "AAPL"
            assert first.side == "sell"  # SELL_STRANGLE
            assert first.alpaca_order_id == "abc123"
            assert first.status == "submitted"  # Alpaca "accepted" normalized to allowed set
            assert len(first.option_legs) == 2

            # Re-emit of the same signal must NOT submit a second order.
            dup = await submit_paper_option_order(sig, 12, session, "k", "s")
            assert dup is None

        count = len(
            (await session.execute(select(BrokerOrder).where(BrokerOrder.broker == "alpaca_options"))).scalars().all()
        )
        assert count == 1  # dedup held

        # Missing legs / strategy → no-op (no broker call).
        assert await submit_paper_option_order({"ticker": "X"}, None, session, "k", "s") is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_resolve_paper_pnl_marks_to_market() -> None:
    session, engine = await _in_memory_session()
    async with session:
        order = BrokerOrder(
            user_id=1,
            broker="paper_options",
            account_type="paper",
            symbol="AAPL",
            notional=200.0,
            side="buy",
            status="filled",
            option_legs=[
                {
                    "option_symbol": "O:AAPL260717C00170000",
                    "position": "long",
                    "quantity": 1,
                    "entry_fill": 2.0,
                }
            ],
            realized_pnl=-0.65,
        )
        session.add(order)
        await session.commit()

        with patch(
            "services.options_paper.fetch_contract_snapshot", new_callable=AsyncMock, return_value=_contract(3.0)
        ):
            await resolve_paper_pnl(session)
            await session.refresh(order)

        # Long call: (3.0 - 2.0) * 1 * 100 = 100 unrealized
        assert order.unrealized_pnl == pytest.approx(100.0)
    await engine.dispose()


@pytest.mark.asyncio
async def test_close_paper_position_realizes_pnl() -> None:
    session, engine = await _in_memory_session()
    async with session:
        order = BrokerOrder(
            user_id=1,
            broker="paper_options",
            account_type="paper",
            symbol="AAPL",
            notional=200.0,
            side="buy",
            status="filled",
            option_legs=[
                {
                    "option_symbol": "O:AAPL260717C00170000",
                    "position": "long",
                    "quantity": 1,
                    "entry_fill": 2.0,
                }
            ],
            fees=0.65,
        )
        session.add(order)
        await session.commit()

        with patch(
            "services.options_paper.fetch_contract_snapshot", new_callable=AsyncMock, return_value=_contract(2.5)
        ):
            closed = await close_paper_position(order, session)
            await session.refresh(closed)

        # Long call: (2.5 - 2.0) * 100 - 0.65 fees = 49.35
        assert closed.final_execution_status == "closed"
        assert closed.realized_pnl == pytest.approx(49.35)
        assert closed.unrealized_pnl == 0.0
    await engine.dispose()
