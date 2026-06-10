import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.gates.base import SignalContext, GatePipeline, GateBase
from services.signal_policy import initialize_policy_and_registry
from models import GateRegistry, SignalPolicy


class DummyGate(GateBase):
    def apply(self, ctx: SignalContext) -> None:
        ctx.score += 5.0
        ctx.confidence = 65.0
        ctx.sources.add("Dummy")
        ctx.rationale.append({"src": "DummyGate", "head": "Dummy Pass", "body": "Dummy gate evaluated successfully"})


class DummyExclusionGate(GateBase):
    def apply(self, ctx: SignalContext) -> None:
        ctx.action = "HOLD"
        ctx.rationale.append({"src": "Risk Gate", "head": "Excluded", "body": "Signal excluded"})


@pytest.mark.asyncio
async def test_gate_tracing_pipeline():
    # Construct context
    ctx = SignalContext(
        action="BUY",
        confidence=50.0,
        score=20.0,
        rationale=[],
        sources=set(),
        ticker="AAPL",
        tech={},
        info={},
        macro={},
        price=150.0,
        atr=3.0,
        has_mr=True,
        vix=18.0,
        sp500_trend="up",
        sector_etf="XLK",
        today_dow=2,
        month=6,
        opt_flow=None,
        sector_rs=None,
        earnings_cal={},
        days_to_earnings=None,
        is_low_atr=False,
        atr_pct_pre=0.02,
    )

    pipeline = GatePipeline([DummyGate(), DummyExclusionGate()])
    pipeline.run(ctx)

    assert len(ctx.gate_traces) == 2

    # First trace
    trace1 = ctx.gate_traces[0]
    assert trace1["gate_id"] == "DummyGate"
    assert trace1["score_delta"] == 5.0
    assert trace1["confidence_delta"] == 15.0
    assert trace1["passed"] is True
    assert trace1["reason"] == "Dummy Pass"

    # Second trace
    trace2 = ctx.gate_traces[1]
    assert trace2["gate_id"] == "DummyExclusionGate"
    assert trace2["passed"] is False
    assert trace2["reason"] == "Excluded"


@pytest.mark.asyncio
async def test_initialize_policy_and_registry():
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_res)

    mock_db = MagicMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    mock_db.return_value.__aexit__.return_value = None

    with patch("services.signal_policy.AsyncSessionLocal", mock_db):
        await initialize_policy_and_registry()

        # Verify additions to db
        added_objs = [call_args[0][0] for call_args in mock_session.add.call_args_list]

        policies = [obj for obj in added_objs if isinstance(obj, SignalPolicy)]
        assert len(policies) == 1
        assert policies[0].version == "v10.5-A16"

        gates = [obj for obj in added_objs if isinstance(obj, GateRegistry)]
        assert len(gates) >= 1

        mock_session.commit.assert_called_once()
