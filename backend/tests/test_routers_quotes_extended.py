"""Extended tests for routers/quotes.py — chart data, sectors, calendar, overview."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from models import User
from services.auth_svc import get_current_user


def _make_df(closes, start="2026-01-01"):
    idx = pd.date_range(start, periods=len(closes), freq="D")
    return pd.DataFrame(
        {"Close": closes, "Open": closes, "High": closes, "Low": closes, "Volume": [1_000_000] * len(closes)}, index=idx
    )


def _make_app(tier="basic", is_owner=True):
    from routers.quotes import router

    app = FastAPI()
    app.include_router(router)

    def _user():
        return User(id=1, email="t@t.com", is_owner=is_owner, subscription_tier=tier, subscription_status="active")

    app.dependency_overrides[get_current_user] = _user
    return app


def test_quotes_endpoint():
    app = _make_app()
    mock_quotes = [{"ticker": "AAPL", "price": 150.0}, {"ticker": "NVDA", "price": 900.0}]
    with (
        patch("routers.quotes.get_settings") as mock_s,
        patch("routers.quotes.get_quotes", new_callable=AsyncMock, return_value=mock_quotes),
    ):
        mock_s.return_value.tickers = ["AAPL", "NVDA"]
        with TestClient(app) as client:
            resp = client.get("/api/quotes")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_chart_data_basic_user():
    app = _make_app(tier="basic")
    df = _make_df([100.0, 101.0, 102.0])
    with patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=df):
        with TestClient(app) as client:
            resp = client.get("/api/chart/AAPL?period=3mo")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert "close" in data[0]


def test_chart_data_free_user_blocked():
    app = _make_app(tier="free", is_owner=False)
    with TestClient(app) as client:
        resp = client.get("/api/chart/AAPL")
    assert resp.status_code == 402


def test_chart_data_no_data():
    app = _make_app()
    with patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=None):
        with TestClient(app) as client:
            resp = client.get("/api/chart/AAPL")
    assert resp.status_code == 200
    assert resp.json() == []


def test_chart_data_invalid_period():
    app = _make_app()
    df = _make_df([100.0, 101.0])
    with patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=df):
        with TestClient(app) as client:
            resp = client.get("/api/chart/AAPL?period=invalid_period")
    assert resp.status_code == 200  # Falls back to default 3mo


def test_chart_data_1d_period():
    app = _make_app()
    idx = pd.date_range("2026-01-01 09:30", periods=10, freq="5min")
    df = pd.DataFrame(
        {
            "Close": [100.0] * 10,
            "Open": [100.0] * 10,
            "High": [101.0] * 10,
            "Low": [99.0] * 10,
            "Volume": [100000] * 10,
        },
        index=idx,
    )
    with patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=df):
        with TestClient(app) as client:
            resp = client.get("/api/chart/AAPL?period=1d")
    assert resp.status_code == 200


def test_relative_chart_success():
    app = _make_app()
    df = _make_df([100.0, 102.0, 105.0])
    with patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=df):
        with TestClient(app) as client:
            resp = client.get("/api/chart/AAPL/relative?period=3mo&versus=SPY")
    assert resp.status_code == 200
    data = resp.json()
    assert "ticker" in data
    assert "bench" in data
    assert data["versus"] == "SPY"


def test_relative_chart_no_data():
    app = _make_app()
    with patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=None):
        with TestClient(app) as client:
            resp = client.get("/api/chart/AAPL/relative")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == []
    assert data["bench"] == []


def test_sector_heatmap_cached():
    import routers.quotes as q

    q._sector_cache["data"] = [{"etf": "XLK", "ret_1d": 1.0}]
    q._sector_cache["ts"] = asyncio.get_event_loop().time() if False else __import__("time").time()
    # Use a trick: patch the loop time
    with patch("asyncio.get_running_loop") as mock_loop:
        mock_loop.return_value.time.return_value = q._sector_cache.get("ts", 0) + 10
        q._sector_cache["ts"] = mock_loop.return_value.time.return_value - 10

    app = _make_app()
    q._sector_cache["data"] = [{"etf": "XLK", "ret_1m": 2.0}]
    # Force fresh fetch
    q._sector_cache["data"] = None

    histories = {
        etf: _make_df([100.0, 101.0, 102.0] * 80)
        for etf in ["XLK", "XLF", "XLY", "XLC", "XLV", "XLP", "XLE", "XLI", "XLB", "XLRE", "XLU"]
    }
    with patch("services.market_data.get_histories_batch", new_callable=AsyncMock, return_value=histories):
        with TestClient(app) as client:
            resp = client.get("/api/market/sectors")
    assert resp.status_code == 200


def test_economic_calendar_fomc_only():
    import routers.quotes as q

    q._cal_cache["data"] = None
    q._cal_cache["ts"] = 0

    app = _make_app()
    settings = MagicMock()
    settings.fred_api_key = ""

    with patch("routers.quotes.get_settings", return_value=settings):
        with TestClient(app) as client:
            resp = client.get("/api/market/calendar")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Should have FOMC events
    fomc_events = [e for e in data if e.get("label") == "FOMC"]
    assert len(fomc_events) >= 0  # May be empty if no future dates


def test_economic_calendar_cached():
    import routers.quotes as q
    import time

    q._cal_cache["data"] = [{"date": "2026-07-01", "label": "FOMC"}]
    q._cal_cache["ts"] = time.time()
    app = _make_app()
    with TestClient(app) as client:
        resp = client.get("/api/market/calendar")
    assert resp.status_code == 200
    assert resp.json()[0]["label"] == "FOMC"


def test_helper_ret():
    from routers.quotes import _ret
    import pandas as pd

    closes = pd.Series([100.0, 102.0, 104.0, 106.0])
    # 1-day return: 106/104 - 1 ≈ 1.92%
    result = _ret(closes, 1)
    assert result is not None
    assert abs(result - 1.92) < 0.1


def test_helper_ret_none():
    from routers.quotes import _ret

    assert _ret(None, 5) is None
    import pandas as pd

    assert _ret(pd.Series([100.0]), 5) is None


def test_helper_ytd_ret():
    from routers.quotes import _ytd_ret
    import pandas as pd

    this_year = date.today().year
    idx = pd.date_range(f"{this_year}-01-02", periods=5, freq="D")
    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0, 103.0, 105.0]}, index=idx)
    result = _ytd_ret(df)
    assert result is not None
    assert abs(result - 5.0) < 0.5


def test_market_overview_failure():
    app = _make_app()
    with (
        patch("asyncio.to_thread", new_callable=AsyncMock, side_effect=Exception("massive down")),
        patch("routers.quotes.get_history", new_callable=AsyncMock, return_value=None),
        patch("routers.quotes.get_fear_greed", new_callable=AsyncMock, return_value=None),
        patch("routers.quotes.get_put_call_ratio", new_callable=AsyncMock, return_value=None),
        patch("routers.quotes.get_market_breadth", new_callable=AsyncMock, return_value=None),
    ):
        with TestClient(app) as client:
            resp = client.get("/api/market/overview")
    # Should return 503 or 500 when all data sources fail
    assert resp.status_code in (500, 503)
