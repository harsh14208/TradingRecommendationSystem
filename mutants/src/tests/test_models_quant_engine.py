"""Schema tests for the additive quant-engine lifecycle tables.

instruments → bars / feature_snapshots / fills / positions → pnl_daily / risk_metrics

Each test builds an isolated temp-file SQLite engine and create_all()s the full
metadata, so it neither touches the shared test DB nor depends on Alembic.
"""

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import (
    Bar,
    BrokerOrder,
    FeatureSnapshot,
    Fill,
    Instrument,
    PnlDaily,
    Position,
    RiskMetric,
    Signal,
    User,
)


async def _make_session(tmp_path) -> tuple[AsyncSession, object]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/quant.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return maker(), engine


@pytest.mark.asyncio
async def test_full_lifecycle_roundtrip(tmp_path):
    """Persist a complete instrument → signal → order → fill → position → pnl/risk chain."""
    session, engine = await _make_session(tmp_path)
    try:
        user = User(email="quant@example.com", password_hash="x")
        instr = Instrument(ticker="NVDA", name="NVIDIA", sector="Technology", sector_etf="XLK", beta=1.7)
        session.add_all([user, instr])
        await session.flush()  # assign ids

        signal = Signal(ticker="NVDA", action="BUY", confidence=58.0, price=100.0, headline="MR dip", entry=100.0)
        session.add(signal)
        await session.flush()

        now = datetime(2026, 6, 6, 20, 0, tzinfo=timezone.utc)
        session.add_all(
            [
                Bar(instrument_id=instr.id, interval="1d", ts=now, open=99, high=101, low=98, close=100, volume=1e6),
                FeatureSnapshot(
                    instrument_id=instr.id,
                    signal_id=signal.id,
                    ts=now,
                    rsi=28.0,
                    bb_pct_b=0.12,
                    ibs=0.10,
                    quality_score=46.0,
                    features={"vwap_pct": -1.1, "atr_pct": 3.2},
                ),
            ]
        )

        order = BrokerOrder(
            signal_id=signal.id,
            user_id=user.id,
            broker="ibkr",
            account_type="paper",
            symbol="NVDA",
            notional=1000.0,
            side="buy",
            status="filled",
        )
        session.add(order)
        await session.flush()

        session.add(
            Fill(
                broker_order_id=order.id,
                user_id=user.id,
                instrument_id=instr.id,
                side="buy",
                qty=10.0,
                price=100.0,
                commission=0.0,
                slippage_bps=1.5,
            )
        )
        position = Position(
            user_id=user.id,
            instrument_id=instr.id,
            signal_id=signal.id,
            status="open",
            side="long",
            qty=10.0,
            avg_entry_price=100.0,
            cost_basis=1000.0,
            last_price=104.0,
            market_value=1040.0,
            unrealized_pnl=40.0,
            stop=96.0,
            target=110.0,
        )
        session.add(position)
        session.add_all(
            [
                PnlDaily(
                    user_id=user.id,
                    date=date(2026, 6, 6),
                    equity=10040.0,
                    cash=9000.0,
                    realized_pnl=0.0,
                    unrealized_pnl=40.0,
                    gross_exposure=1040.0,
                    net_exposure=1040.0,
                    drawdown_pct=0.0,
                    n_positions=1,
                ),
                RiskMetric(
                    user_id=user.id,
                    date=date(2026, 6, 6),
                    portfolio_beta=1.7,
                    portfolio_vol=0.22,
                    var_95=-180.0,
                    max_sector_pct=1.0,
                    avg_pairwise_corr=0.0,
                    gross_leverage=0.10,
                    net_leverage=0.10,
                ),
            ]
        )
        await session.commit()

        # Round-trip reads
        got_instr = (await session.execute(select(Instrument).where(Instrument.ticker == "NVDA"))).scalar_one()
        assert got_instr.beta == 1.7 and got_instr.is_active is True and got_instr.currency == "USD"

        feat = (await session.execute(select(FeatureSnapshot))).scalar_one()
        assert feat.signal_id == signal.id and feat.features["vwap_pct"] == -1.1 and feat.rsi == 28.0

        fill = (await session.execute(select(Fill))).scalar_one()
        assert fill.broker_order_id == order.id and fill.qty == 10.0

        pos = (await session.execute(select(Position).where(Position.user_id == user.id))).scalar_one()
        assert pos.unrealized_pnl == 40.0 and pos.status == "open" and pos.realized_pnl == 0.0

        pnl = (await session.execute(select(PnlDaily))).scalar_one()
        assert pnl.equity == 10040.0 and pnl.n_positions == 1

        risk = (await session.execute(select(RiskMetric))).scalar_one()
        assert risk.portfolio_beta == 1.7 and risk.var_95 == -180.0
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_instrument_ticker_unique(tmp_path):
    session, engine = await _make_session(tmp_path)
    try:
        session.add(Instrument(ticker="AAPL"))
        await session.commit()
        session.add(Instrument(ticker="AAPL"))
        with pytest.raises(IntegrityError):
            await session.commit()
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_bars_unique_per_instrument_interval_ts(tmp_path):
    session, engine = await _make_session(tmp_path)
    try:
        instr = Instrument(ticker="MSFT")
        session.add(instr)
        await session.flush()
        ts = datetime(2026, 6, 6, tzinfo=timezone.utc)
        session.add(Bar(instrument_id=instr.id, interval="1d", ts=ts, open=1, high=1, low=1, close=1, volume=1))
        await session.commit()
        # Same (instrument, interval, ts) → uq_bars_instrument_interval_ts violation
        session.add(Bar(instrument_id=instr.id, interval="1d", ts=ts, open=2, high=2, low=2, close=2, volume=2))
        with pytest.raises(IntegrityError):
            await session.commit()
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_pnl_daily_unique_user_date(tmp_path):
    session, engine = await _make_session(tmp_path)
    try:
        user = User(email="dup@example.com", password_hash="x")
        session.add(user)
        await session.flush()
        d = date(2026, 6, 6)
        session.add(PnlDaily(user_id=user.id, date=d, equity=100.0))
        await session.commit()
        session.add(PnlDaily(user_id=user.id, date=d, equity=200.0))
        with pytest.raises(IntegrityError):
            await session.commit()
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_defaults_applied(tmp_path):
    """Server/Python defaults populate without explicit values."""
    session, engine = await _make_session(tmp_path)
    try:
        instr = Instrument(ticker="TSLA")  # asset_type/currency/is_active defaulted
        session.add(instr)
        await session.flush()
        pos = Position(user_id=None, instrument_id=instr.id, avg_entry_price=50.0)  # status/side/qty defaulted
        # user_id is nullable=False; give it a user
        user = User(email="d@example.com", password_hash="x")
        session.add(user)
        await session.flush()
        pos.user_id = user.id
        session.add(pos)
        await session.commit()
        await session.refresh(instr)
        await session.refresh(pos)
        assert instr.asset_type == "equity" and instr.currency == "USD" and instr.is_active is True
        assert pos.status == "open" and pos.side == "long" and pos.qty == 0 and pos.realized_pnl == 0
    finally:
        await session.close()
        await engine.dispose()
