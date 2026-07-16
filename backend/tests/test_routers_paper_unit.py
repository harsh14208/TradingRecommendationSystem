"""Tests for routers/paper_router.py — paper trading via Alpaca."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr


def _make_app(has_keys=True):
    from routers.paper_router import router
    from services.auth_svc import get_current_user

    app = FastAPI()
    app.include_router(router)

    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.is_owner = False
    mock_user.subscription_tier = "pro"
    mock_user.subscription_status = "active"
    app.dependency_overrides[get_current_user] = lambda: mock_user

    settings = MagicMock()
    settings.alpaca_api_key = SecretStr("test_key") if has_keys else ""
    settings.alpaca_api_secret = SecretStr("test_secret") if has_keys else SecretStr("")

    with patch("routers.paper_router.get_settings", return_value=settings):
        return app, settings


def test_account_no_keys():
    app, _ = _make_app(has_keys=False)
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = ""
        mock_s.return_value.alpaca_api_secret = ""
        with TestClient(app) as client:
            resp = client.get("/api/paper/account")
    assert resp.status_code == 403


def test_account_success():
    account_data = {"equity": "10000.00", "buying_power": "8000.00"}
    app, _ = _make_app(has_keys=True)
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=account_data),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/account")
    assert resp.status_code == 200
    assert resp.json()["equity"] == "10000.00"


def test_account_upstream_error():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, side_effect=Exception("upstream down")),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/account")
    assert resp.status_code == 502


def test_positions_no_keys():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = ""
        mock_s.return_value.alpaca_api_secret = ""
        with TestClient(app) as client:
            resp = client.get("/api/paper/positions")
    assert resp.status_code == 403


def test_positions_success():
    positions = [{"symbol": "AAPL", "qty": "10", "market_value": "1500.00"}]
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=positions),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/positions")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_orders_no_keys():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = ""
        mock_s.return_value.alpaca_api_secret = ""
        with TestClient(app) as client:
            resp = client.get("/api/paper/orders")
    assert resp.status_code == 403


def test_orders_success():
    orders = [{"id": "abc", "symbol": "NVDA", "qty": "5"}]
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_orders", new_callable=AsyncMock, return_value=orders),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/orders?status=open")
    assert resp.status_code == 200


def test_place_order_invalid_side():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.post("/api/paper/orders", json={"symbol": "AAPL", "qty": 10, "side": "hold"})
    assert resp.status_code == 400


def test_place_order_invalid_qty():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.post("/api/paper/orders", json={"symbol": "AAPL", "qty": 0, "side": "buy"})
    assert resp.status_code == 400


def test_place_order_success():
    # Use a unique Alpaca order id so repeated local test runs don't collide on
    # the broker_orders.alpaca_order_id unique constraint.
    order = {"id": f"order-{uuid.uuid4().hex[:8]}", "symbol": "AAPL", "status": "accepted"}
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch(
            "services.alpaca_rest.get_account",
            new_callable=AsyncMock,
            return_value={
                "non_marginable_buying_power": "100000",
                "cash": "100000",
            },
        ),
        patch("services.market_data.get_quote", new_callable=AsyncMock, return_value={"p": 150.0}),
        patch("services.alpaca_rest.place_order", new_callable=AsyncMock, return_value=order),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.post("/api/paper/orders", json={"symbol": "AAPL", "qty": 10, "side": "buy"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


def test_place_order_buy_exceeds_non_margin_bp():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch(
            "services.alpaca_rest.get_account",
            new_callable=AsyncMock,
            return_value={"non_marginable_buying_power": "100", "cash": "100"},
        ),
        patch("services.market_data.get_quote", new_callable=AsyncMock, return_value={"p": 150.0}),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.post("/api/paper/orders", json={"symbol": "AAPL", "qty": 10, "side": "buy"})
    assert resp.status_code == 400
    assert "non-margin buying power" in resp.json()["detail"].lower()


def test_place_order_sell_naked_short_rejected():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch(
            "services.alpaca_rest.get_account",
            new_callable=AsyncMock,
            return_value={"non_marginable_buying_power": "100000", "cash": "100000"},
        ),
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=[]),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.post("/api/paper/orders", json={"symbol": "AAPL", "qty": 10, "side": "sell"})
    assert resp.status_code == 400
    assert "naked short" in resp.json()["detail"].lower()


def test_close_position_success():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.close_position", new_callable=AsyncMock, return_value={"status": "closed"}),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.delete("/api/paper/positions/AAPL")
    assert resp.status_code == 200


def test_cancel_order_success():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.cancel_order", new_callable=AsyncMock, return_value={"status": "cancelled"}),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.delete("/api/paper/orders/order123")
    assert resp.status_code == 200


def test_portfolio_risk_no_positions():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=[]),
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value={"equity": "10000"}),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/risk")
    assert resp.status_code == 200
    assert resp.json()["positions"] == 0
    assert resp.json()["risk_level"] == "none"


def test_volatility_target():
    result = {"weights": {"SPY": 0.3, "QQQ": 0.25}, "target_vol": 0.15}
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch(
            "services.volatility_targeting.get_volatility_target_weights", new_callable=AsyncMock, return_value=result
        ),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/volatility-target?tickers=SPY,QQQ")
    assert resp.status_code == 200


def test_volatility_target_error():
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch(
            "services.volatility_targeting.get_volatility_target_weights",
            new_callable=AsyncMock,
            return_value={"error": "insufficient data"},
        ),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/volatility-target")
    assert resp.status_code == 400


def test_cot_account_no_keys():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        mock_s.return_value.alpaca_se_api_key = ""
        mock_s.return_value.alpaca_se_api_secret = SecretStr("")
        with TestClient(app) as client:
            resp = client.get("/api/paper/cot/account")
    assert resp.status_code == 403


def test_cot_account_success():
    account_data = {"equity": "250000.00", "buying_power": "200000.00"}
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=account_data),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        mock_s.return_value.alpaca_se_api_key = SecretStr("se_key")
        mock_s.return_value.alpaca_se_api_secret = SecretStr("se_secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/cot/account")
    assert resp.status_code == 200
    assert resp.json()["equity"] == "250000.00"


def test_cot_positions_success():
    positions = [{"symbol": "SPY", "qty": "50", "market_value": "25000.00"}]
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=positions),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        mock_s.return_value.alpaca_se_api_key = SecretStr("se_key")
        mock_s.return_value.alpaca_se_api_secret = SecretStr("se_secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/cot/positions")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_cot_orders_success():
    orders = [{"id": "cot1", "symbol": "QQQ", "qty": "10"}]
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_orders", new_callable=AsyncMock, return_value=orders),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        mock_s.return_value.alpaca_se_api_key = SecretStr("se_key")
        mock_s.return_value.alpaca_se_api_secret = SecretStr("se_secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/cot/orders?status=open")
    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "cot1"


def test_cot_risk_success():
    risk_data = {
        "positions": 2,
        "total_exposure": 50000.0,
        "exposure_pct": 50.0,
        "benchmark": "SPY",
        "beta": 1.1,
        "sharpe": 0.85,
        "max_drawdown": -5.2,
        "risk_level": "medium",
        "observations": 240,
    }
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value={"equity": "100000.00"}),
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=[]),
        patch("services.portfolio_risk.compute_portfolio_risk", new_callable=AsyncMock, return_value=risk_data),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        mock_s.return_value.alpaca_se_api_key = SecretStr("se_key")
        mock_s.return_value.alpaca_se_api_secret = SecretStr("se_secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/cot/risk")
    assert resp.status_code == 200
    assert resp.json()["beta"] == 1.1


def test_equity_risk_success():
    risk_data = {
        "positions": 3,
        "total_exposure": 75000.0,
        "exposure_pct": 75.0,
        "benchmark": "SPY",
        "beta": 1.25,
        "sharpe": 1.05,
        "max_drawdown": -8.5,
        "risk_level": "medium",
        "observations": 240,
    }
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value={"equity": "100000.00"}),
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=[]),
        patch("services.portfolio_risk.compute_portfolio_risk", new_callable=AsyncMock, return_value=risk_data),
    ):
        mock_s.return_value.alpaca_api_key = SecretStr("key")
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/risk")
    assert resp.status_code == 200
    assert resp.json()["sharpe"] == 1.05
