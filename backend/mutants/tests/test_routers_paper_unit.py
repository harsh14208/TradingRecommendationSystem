"""Tests for routers/paper_router.py — paper trading via Alpaca."""

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
    settings.alpaca_api_key = "test_key" if has_keys else ""
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
        mock_s.return_value.alpaca_api_key = "key"
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
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/account")
    assert resp.status_code == 502


def test_positions_no_keys():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = ""
        with TestClient(app) as client:
            resp = client.get("/api/paper/positions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_positions_success():
    positions = [{"symbol": "AAPL", "qty": "10", "market_value": "1500.00"}]
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=positions),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.get("/api/paper/positions")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_orders_no_keys():
    app, _ = _make_app()
    with patch("routers.paper_router.get_settings") as mock_s:
        mock_s.return_value.alpaca_api_key = ""
        with TestClient(app) as client:
            resp = client.get("/api/paper/orders")
    assert resp.status_code == 200
    assert resp.json() == []


def test_orders_success():
    orders = [{"id": "abc", "symbol": "NVDA", "qty": "5"}]
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.get_orders", new_callable=AsyncMock, return_value=orders),
    ):
        mock_s.return_value.alpaca_api_key = "key"
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
    order = {"id": "xyz", "symbol": "AAPL", "status": "accepted"}
    app, _ = _make_app()
    with (
        patch("routers.paper_router.get_settings") as mock_s,
        patch("services.alpaca_rest.place_order", new_callable=AsyncMock, return_value=order),
    ):
        mock_s.return_value.alpaca_api_key = "key"
        mock_s.return_value.alpaca_api_secret = SecretStr("secret")
        with TestClient(app) as client:
            resp = client.post("/api/paper/orders", json={"symbol": "AAPL", "qty": 10, "side": "buy"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


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
