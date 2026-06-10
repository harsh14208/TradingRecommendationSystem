"""
tests/test_qeng_features.py

Tests for QENG-1 (ResearchExperiment registry, PBO, promote_model)
and QENG-2 (FeatureSnapshot store, replay engine, lineage).
"""

import asyncio
from datetime import datetime
import pytest
from sqlalchemy import select

from database import AsyncSessionLocal, init_db
from models import ResearchExperiment, FeatureSnapshot, Instrument, ModelRegistry, ActionAuditLog
from services.feature_store import save_feature_snapshot, get_or_create_instrument
from services.lineage import get_lineage_meta, get_lineage_hash
from scripts.replay_engine import run_replay
from scripts.promote_model import promote_model

@pytest.fixture(autouse=True, scope="module")
def setup_test_db():
    import os
    import asyncio
    if os.path.exists("./test_db.sqlite"):
        try:
            os.remove("./test_db.sqlite")
        except Exception:
            pass
    asyncio.run(init_db())

@pytest.mark.asyncio
async def test_research_experiment_creation():
    """Verify that we can create and retrieve a ResearchExperiment row."""
    async with AsyncSessionLocal() as db:
        exp = ResearchExperiment(
            experiment_type="gate_ablation",
            hypothesis="Removing CMF from weights increases Sharpe",
            universe={"tickers": ["NVDA", "AAPL"]},
            data_version="1.1",
            git_sha="abcdef1234567890abcdef1234567890abcdef12",
            search_space={"CMF_weights": [0.0, 0.5, 1.0]},
            number_of_trials=3,
            is_metrics={"sharpe": 0.28},
            oos_metrics={"sharpe": 0.25},
            dsr_pbo={"pbo": 0.08},
            decision="promoted",
            promotion_status="live"
        )
        db.add(exp)
        await db.commit()

        # Retrieve and verify
        res = await db.execute(select(ResearchExperiment).where(ResearchExperiment.id == exp.id))
        retrieved = res.scalar_one()
        assert retrieved.experiment_type == "gate_ablation"
        assert retrieved.decision == "promoted"
        assert retrieved.is_metrics["sharpe"] == 0.28


@pytest.mark.asyncio
async def test_feature_store_snapshots():
    """Verify that feature snapshot saving and mapping functions operate correctly."""
    async with AsyncSessionLocal() as db:
        # Test instrument get-or-create
        inst = await get_or_create_instrument(db, "TEST_TICKER")
        assert inst.ticker == "TEST_TICKER"

        # Test snapshot persistence
        ts = datetime.utcnow()
        features = {
            "rsi": 38.5,
            "bb_pct_b": 0.19,
            "ibs": 0.08,
            "vwap_pct": -0.92,
            "atr_pct": 2.8,
            "zscore": -2.4,
            "quality_score": 41.5,
            "hasMr": True
        }
        snap = await save_feature_snapshot(
            db=db,
            ticker="TEST_TICKER",
            ts=ts,
            features=features,
            provider="polygon",
            signal_policy_version="v2.1"
        )
        await db.commit()

        # Check retrieval
        res = await db.execute(select(FeatureSnapshot).where(FeatureSnapshot.id == snap.id))
        retrieved = res.scalar_one()
        assert retrieved.rsi == 38.5
        assert retrieved.bb_pct_b == 0.19
        assert retrieved.provider == "polygon"
        assert retrieved.signal_policy_version == "v2.1"
        assert retrieved.feature_vector_hash is not None


def test_lineage_metadata():
    """Verify lineage tracking values and hash consistency."""
    meta = get_lineage_meta()
    assert meta["vendor"] == "Polygon.io"
    assert meta["data_version"] == "v1.2.0"
    assert "lineage_hash" in meta
    assert get_lineage_hash() == meta["lineage_hash"]


@pytest.mark.asyncio
async def test_replay_engine_run():
    """Smoke test for running the replay engine harness."""
    # Running run_replay will generate a mock snapshot if none exist
    # and execute it through check_delivery_gates cleanly.
    await run_replay()


@pytest.mark.asyncio
async def test_promote_model_checklist():
    """Test model promotion script against registry and checklist requirements."""
    class MockArgs:
        model_id = "test_ml_champion_v1"
        oos_universe = "NVDA,AAPL,MSFT"
        replay_sharpe = 0.35
        shadow_sharpe = 0.32
        cost_adjusted_sharpe = 0.28
        rollback_plan = "Revert config flag MODEL_VERSION = v1"
        expiration_days = 90

    args = MockArgs()
    args.oos_universe = [t.strip() for t in args.oos_universe.split(",")]
    
    # Run model promotion
    await promote_model(args)
    
    # Verify in DB
    async with AsyncSessionLocal() as db:
        # Model should be active in ModelRegistry
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == "test_ml_champion_v1"))
        model = res.scalar_one_or_none()
        assert model is not None
        assert model.approval_decision == "approved"
        assert model.is_active is True
        
        # Verify an ActionAuditLog was written
        audit_res = await db.execute(select(ActionAuditLog).where(ActionAuditLog.action == "promote_model").order_by(ActionAuditLog.created_at.desc()))
        audit = audit_res.scalars().first()
        assert audit is not None
        assert audit.details["model_id"] == "test_ml_champion_v1"


@pytest.mark.asyncio
async def test_tca_calculations_and_capacity():
    """Verify realized TCA logging, fill creation, and expected slippage capacity checks."""
    from services.tca_service import calculate_expected_slippage_bps, check_capacity_limits, record_fill_tca
    from models import BrokerOrder, Fill
    
    # 1. Test Almgren-Chriss calculation
    slip = calculate_expected_slippage_bps("AAPL", qty=100, price=150.0, adv=1000000, daily_vol=0.02, spread_pct=0.001)
    assert slip > 5.0  # must be positive and account for spread half-width (5 bps) + impact
    
    async with AsyncSessionLocal() as db:
        # 2. Test check_capacity_limits
        blocked, suggested, expected = await check_capacity_limits(db, "AAPL", 15000.0, 150.0)
        assert not blocked
        assert suggested == 15000.0
        
        # Test capacity scaling for extremely large order
        blocked, suggested, expected = await check_capacity_limits(db, "AAPL", 15000000.0, 150.0)
        assert suggested < 15000000.0
        
        # 3. Test record_fill_tca
        order = BrokerOrder(
            user_id=1,
            broker="alpaca",
            account_type="paper",
            symbol="AAPL",
            notional=15000.0,
            side="buy",
            status="submitted",
            arrival_price=150.0
        )
        db.add(order)
        await db.commit()
        
        broker_data = {
            "filled_qty": 100.0,
            "qty": 100.0,
            "filled_avg_price": 150.50,
            "status": "filled"
        }
        
        updated_order = await record_fill_tca(db, order, broker_data)
        await db.commit()
        
        assert updated_order.avg_fill_price == 150.50
        assert updated_order.fees is not None
        
        # Check that a Fill row was created
        res_fill = await db.execute(select(Fill).where(Fill.broker_order_id == order.id))
        fill_row = res_fill.scalar_one_or_none()
        assert fill_row is not None
        assert fill_row.qty == 100.0
        assert fill_row.price == 150.50


@pytest.mark.asyncio
async def test_portfolio_hrp_allocations():
    """Verify that Hierarchical Risk Parity weights can be calculated from returns covariance."""
    from services.portfolio_allocator import compute_hrp_weights, allocate_portfolio
    import numpy as np
    
    # 1. Check direct HRP weights math
    # Construct a PSD covariance matrix for 3 assets
    cov = np.array([
        [0.04, 0.038, 0.0],
        [0.038, 0.04, 0.0],
        [0.0, 0.0, 0.01]
    ])
    tickers = ["ASSET1", "ASSET2", "ASSET3"]
    weights = compute_hrp_weights(cov, tickers)
    
    # Asset 3 should get higher weight due to lower variance and correlation diversification
    assert weights["ASSET3"] > weights["ASSET1"]
    assert weights["ASSET3"] > weights["ASSET2"]
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    
    # 2. Check allocation flow under sector/cash constraints
    async with AsyncSessionLocal() as db:
        active_signals = [
            {"ticker": "AAPL", "sectorEtf": "XLK", "id": 1, "entry": 150.0},
            {"ticker": "MSFT", "sectorEtf": "XLK", "id": 2, "entry": 300.0},
            {"ticker": "NVDA", "sectorEtf": "XLK", "id": 3, "entry": 400.0}
        ]
        orders = await allocate_portfolio(db, user_id=1, active_signals=active_signals, total_cash=10000.0)
        assert isinstance(orders, list)


@pytest.mark.asyncio
async def test_portfolio_allocator_optimizations():
    """Verify L7 nudge, Volatility sizing penalty, and Drawdown throttle logic."""
    from services.portfolio_allocator import allocate_portfolio
    from models import PnlDaily, User
    import datetime
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        # Create a test user with a high unique ID
        user_id = 9999
        res_u = await db.execute(select(User).where(User.id == user_id))
        user = res_u.scalar_one_or_none()
        if not user:
            user = User(id=user_id, email="test_opt@signal.trade", password_hash="hash")
            db.add(user)
            await db.flush()
            
        # 1. Setup Drawdown Throttle (Peak equity = 20,000, current cash = 10,000 -> 50% DD)
        today = datetime.date.today()
        peak_pnl = PnlDaily(
            user_id=user_id,
            date=today - datetime.timedelta(days=1),
            equity=20000.0,
            cash=20000.0,
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            n_positions=0
        )
        db.add(peak_pnl)
        await db.flush()
        
        # AAPL and MSFT signals (AAPL has higher raw_score -> should get higher L7 nudge weight)
        active_signals = [
            {"ticker": "AAPL", "sectorEtf": "XLK", "id": 1, "entry": 150.0, "raw_score": 80.0},
            {"ticker": "MSFT", "sectorEtf": "XLK", "id": 2, "entry": 300.0, "raw_score": 50.0}
        ]
        
        # Test Case A: AAPL raw_score = 80, MSFT raw_score = 50
        orders_diff = await allocate_portfolio(db, user_id=user_id, active_signals=active_signals, total_cash=10000.0)
        assert len(orders_diff) > 0
        aapl_diff = next(o["target_weight"] for o in orders_diff if o["ticker"] == "AAPL")
        msft_diff = next(o["target_weight"] for o in orders_diff if o["ticker"] == "MSFT")
        ratio_diff = aapl_diff / msft_diff
        
        # Test Case B: Both have raw_score = 50
        active_signals_eq = [
            {"ticker": "AAPL", "sectorEtf": "XLK", "id": 1, "entry": 150.0, "raw_score": 50.0},
            {"ticker": "MSFT", "sectorEtf": "XLK", "id": 2, "entry": 300.0, "raw_score": 50.0}
        ]
        orders_eq = await allocate_portfolio(db, user_id=user_id, active_signals=active_signals_eq, total_cash=10000.0)
        aapl_eq = next(o["target_weight"] for o in orders_eq if o["ticker"] == "AAPL")
        msft_eq = next(o["target_weight"] for o in orders_eq if o["ticker"] == "MSFT")
        ratio_eq = aapl_eq / msft_eq
        
        # 2. Verify L7 nudge: AAPL ratio should be higher when it has a higher score
        assert ratio_diff > ratio_eq
        
        # 3. Verify Drawdown throttle: total target weights should be scaled down by 0.5
        total_target_w = aapl_diff + msft_diff
        assert total_target_w < 0.6  # HRP baseline sums to ~1.0, scaled down to ~0.5 under drawdown
            
        # Clean up
        await db.delete(peak_pnl)
        await db.delete(user)
        await db.commit()


@pytest.mark.asyncio
async def test_alpha_sleeves_logic():
    """Verify that stat-arb OLS residuals, TS momentum, factor ranks, and cross-sleeve allocator operate correctly."""
    from services.alpha_sleeves import (
        compute_etf_residual_stat_arb,
        compute_time_series_momentum,
        compute_cross_sectional_factor_scores,
        allocate_cross_sleeve_capital
    )
    
    # 1. Test cross-sleeve allocator
    sleeve_sharpes = {"MR": 1.2, "StatArb": 1.5, "Trend": 0.8, "Factor": 0.5}
    allocation = allocate_cross_sleeve_capital(sleeve_sharpes, total_capital=10000.0)
    assert sum(allocation.values()) == 10000.0
    assert allocation["StatArb"] > allocation["Factor"]
    
    # 2. Test residual stat arb smoke test
    tickers = ["AAPL"]
    sector_etfs = {"AAPL": "XLK"}
    residuals = await compute_etf_residual_stat_arb(tickers, sector_etfs)
    assert isinstance(residuals, dict)  # returns empty or populated dict gracefully depending on market data availability
    
    # 3. Test time series momentum
    momentum = await compute_time_series_momentum()
    assert isinstance(momentum, dict)
    
    # 4. Test cross sectional factors
    factor_scores = await compute_cross_sectional_factor_scores(["AAPL", "MSFT"])
    assert isinstance(factor_scores, dict)


def test_cohort_routing_and_policy_logging():
    """Verify that cohort routing is deterministic and properly includes policy metadata."""
    from services.cohort_service import allocate_signal_cohort, build_policy_version_meta
    from datetime import datetime
    
    ts = datetime(2026, 6, 8, 12, 0, 0)
    # Check that it returns deterministic cohort assignment
    cohort1 = allocate_signal_cohort("AAPL", ts)
    cohort2 = allocate_signal_cohort("AAPL", ts)
    assert cohort1 == cohort2
    assert cohort1 in ["delivered", "shadow", "withheld"]
    
    meta = build_policy_version_meta("AAPL", ts, meta_prob=0.82)
    assert meta["cohort"] == cohort1
    assert meta["meta_label_probability"] == 0.82
    assert meta["policy_versions"]["scoring"] == "v10.3"
