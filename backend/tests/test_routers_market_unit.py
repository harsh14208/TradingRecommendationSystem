"""Tests for routers/market.py — covers all endpoints with mocked services."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _make_app():
    from routers.market import router

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client():
    return TestClient(_make_app())


def test_market_context_fresh(client):
    import routers.market as m

    m._ctx_cache["data"] = None
    m._ctx_cache["ts"] = 0.0
    with (
        patch("routers.market.get_fear_greed", new_callable=AsyncMock, return_value={"score": 42}),
        patch("routers.market.get_macro_context", new_callable=AsyncMock, return_value={"vix": 18}),
        patch("routers.market.get_put_call_ratio", new_callable=AsyncMock, return_value={"ratio": 0.8}),
        patch("routers.market.get_market_breadth", new_callable=AsyncMock, return_value={"pct_above_200d": 60}),
        patch("routers.market.get_aaii_sentiment", new_callable=AsyncMock, return_value={"bullish": 40}),
        patch("routers.market.get_cot_signal", new_callable=AsyncMock, return_value={"signal": "neutral"}),
        patch("routers.market.get_api_usage", return_value={"finnhub": 10}),
        patch("services.macro_regime.get_macro_regime", new_callable=AsyncMock, return_value={"regime": "bull"}),
    ):
        resp = client.get("/api/market/context")
    assert resp.status_code == 200
    data = resp.json()
    assert "fear_greed" in data
    assert "macro" in data


def test_market_context_cached(client):
    import routers.market as m
    import time

    m._ctx_cache["data"] = {"cached": True}
    m._ctx_cache["ts"] = time.monotonic()
    resp = client.get("/api/market/context")
    assert resp.status_code == 200
    assert resp.json()["cached"] is True


def test_market_context_with_exceptions(client):
    import routers.market as m

    m._ctx_cache["data"] = None
    m._ctx_cache["ts"] = 0.0
    with (
        patch("routers.market.get_fear_greed", new_callable=AsyncMock, side_effect=Exception("fail")),
        patch("routers.market.get_macro_context", new_callable=AsyncMock, return_value=None),
        patch("routers.market.get_put_call_ratio", new_callable=AsyncMock, return_value=None),
        patch("routers.market.get_market_breadth", new_callable=AsyncMock, return_value=None),
        patch("routers.market.get_aaii_sentiment", new_callable=AsyncMock, return_value=None),
        patch("routers.market.get_cot_signal", new_callable=AsyncMock, return_value=None),
        patch("routers.market.get_api_usage", return_value={}),
        patch("services.macro_regime.get_macro_regime", new_callable=AsyncMock, return_value=None),
    ):
        resp = client.get("/api/market/context")
    assert resp.status_code == 200
    assert resp.json()["fear_greed"] is None


def test_macro_regime_endpoint(client):
    with patch(
        "services.macro_regime.get_macro_regime", new_callable=AsyncMock, return_value={"regime": "bear", "bull_p": 0.1}
    ):
        resp = client.get("/api/market/regime")
    assert resp.status_code == 200
    assert resp.json()["regime"] == "bear"


def test_invalidate_regime_cache(client):
    with patch("services.macro_regime.invalidate_cache") as mock_inv:
        resp = client.post("/api/market/regime/invalidate")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    mock_inv.assert_called_once()


def test_supply_chain_endpoint(client):
    with patch(
        "services.supply_chain.get_supply_chain_signals",
        new_callable=AsyncMock,
        return_value={"bdi": 1200, "signals": []},
    ):
        resp = client.get("/api/market/supply-chain")
    assert resp.status_code == 200


def test_dark_pool_endpoint(client):
    with patch(
        "services.dark_pool.get_reconstructed_orders",
        new_callable=AsyncMock,
        return_value=[{"ticker": "AAPL", "size": 10000}],
    ):
        resp = client.get("/api/market/dark-pool/reconstructed?ticker=AAPL")
    assert resp.status_code == 200


def test_dark_pool_no_ticker(client):
    with patch("services.dark_pool.get_reconstructed_orders", new_callable=AsyncMock, return_value=[]):
        resp = client.get("/api/market/dark-pool/reconstructed")
    assert resp.status_code == 200


def test_corporate_events_endpoint(client):
    with patch(
        "services.corporate_events.get_corporate_events",
        new_callable=AsyncMock,
        return_value=[{"event": "earnings", "ticker": "NVDA"}],
    ):
        resp = client.get("/api/market/events")
    assert resp.status_code == 200


def test_etf_flows_endpoint(client):
    with patch("services.etf_flows.get_etf_flows", new_callable=AsyncMock, return_value={"XLK": {"flow": 100}}):
        resp = client.get("/api/market/etf-flows")
    assert resp.status_code == 200


def test_etf_constituents_endpoint(client):
    with patch(
        "services.etf_constituents.get_etf_constituents",
        new_callable=AsyncMock,
        return_value=[{"ticker": "AAPL", "weight": 0.12}],
    ):
        resp = client.get("/api/market/etf-constituents/XLK")
    assert resp.status_code == 200


def test_economy_endpoint(client):
    with patch("services.massive_economy.get_economy_data", new_callable=AsyncMock, return_value={"cpi": 3.1}):
        resp = client.get("/api/market/economy")
    assert resp.status_code == 200


def test_analyst_endpoint(client):
    with patch(
        "services.massive_analyst.get_analyst_intelligence",
        new_callable=AsyncMock,
        return_value={"rating": "buy", "target": 200},
    ):
        resp = client.get("/api/market/analyst/NVDA")
    assert resp.status_code == 200


def test_eightk_endpoint(client):
    with patch("services.eightk_events.get_8k_signals", new_callable=AsyncMock, return_value=[{"event": "merger"}]):
        resp = client.get("/api/market/8k/AAPL")
    assert resp.status_code == 200


def test_options_endpoint(client):
    with patch(
        "services.massive_options.get_option_chain_signals",
        new_callable=AsyncMock,
        return_value={"gex": -500, "max_pain": 150},
    ):
        resp = client.get("/api/market/options/NVDA?price=150.0")
    assert resp.status_code == 200
