"""Tests for the research backtest endpoint and service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import Signal, User
from routers.signals import router
from services.auth_svc import get_current_user
from services.backtest_research_svc import clear_research_cache, get_research_backtest


def _make_user():
    return User(id=1, email="test@example.com", is_owner=False)


def _make_app_with_overrides(mock_db_session):
    app = FastAPI()
    app.include_router(router, prefix="")
    app.dependency_overrides[get_current_user] = _make_user

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


def test_research_service_returns_canon_structure():
    """The research service loads CSVs and returns the expected payload shape."""
    clear_research_cache()
    payload = get_research_backtest()
    assert "canon" in payload
    assert "summary" in payload
    assert "equity_curve" in payload
    assert "trades" in payload
    assert isinstance(payload["equity_curve"], list)
    assert isinstance(payload["trades"], list)
    # Canon constants are always present as cross-check labels.
    assert payload["canon"]["total_trades"] == 217
    assert payload["canon"]["win_rate"] == 69.1
    assert payload["canon"]["sharpe"] == 0.24


def test_research_endpoint_returns_200():
    mock_db_session = MagicMock()
    mock_db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    )
    app = _make_app_with_overrides(mock_db_session)

    with TestClient(app) as client:
        res = client.get("/api/signals/backtest/research")
        assert res.status_code == 200
        body = res.json()
        assert body["canon"]["total_trades"] == 217


def test_simulate_endpoint_accepts_entry_policy_and_max_signals():
    """The simulator passes new query params through to the simulation logic."""
    mock_db_session = MagicMock()

    sig = MagicMock(spec=Signal)
    sig.id = 1
    sig.ticker = "AAPL"
    sig.action = "BUY"
    sig.entry = 100.0
    sig.stop = 95.0
    sig.target = 105.0
    sig.created_at = datetime(2024, 1, 1)
    sig.outcome_pct = None

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sig]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    app = _make_app_with_overrides(mock_db_session)

    import pandas as pd

    fake_df = pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104, 105, 106, 107],
            "High": [101, 102, 103, 104, 105, 106, 107, 108],
            "Low": [99, 100, 101, 102, 103, 104, 105, 106],
            "Close": [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5],
        },
        index=pd.date_range("2024-01-02", periods=8, freq="D"),
    )

    with patch("services.market_data.get_history", new=AsyncMock(return_value=fake_df)):
        with TestClient(app) as client:
            res = client.get("/api/signals/backtest/simulate?entry_policy=next_open&max_signals=50")
            assert res.status_code == 200
            body = res.json()
            assert body["entry_policy"] == "next_open"
            assert body["simulated"] == 1
            # With next_open policy and no slippage, actual_entry should equal raw open.
            assert body["signals"][0]["actual_entry"] == 100.0


def test_simulate_endpoint_filters_by_date_range():
    """Date range params are forwarded to the Signal query."""
    mock_db_session = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    app = _make_app_with_overrides(mock_db_session)

    with TestClient(app) as client:
        res = client.get("/api/signals/backtest/simulate?start_date=2024-01-01&end_date=2024-01-31")
        assert res.status_code == 200
        body = res.json()
        assert body["simulated"] == 0

    # Verify the SQL query was constructed with date filters by inspecting the call args.
    call = mock_db_session.execute.call_args
    stmt = call[0][0]
    # The compiled statement should contain the date strings.
    compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    assert "2024-01-01" in compiled
    assert "2024-01-31" in compiled
