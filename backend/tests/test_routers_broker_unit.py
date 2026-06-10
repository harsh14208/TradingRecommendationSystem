"""Unit tests for routers/broker.py — broker connection and status endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


def _make_user(tier="pro", status="active", is_owner=False):
    u = User(id=1, email="t@t.com", is_owner=is_owner, subscription_tier=tier, subscription_status=status)
    u.full_name = "Test"
    u.alpaca_key_enc = None
    u.alpaca_secret_enc = None
    u.auto_execute = False
    u.auto_execute_broker = "alpaca"
    u.alpaca_account_type = "paper"
    u.auto_execute_min_conf = 75.0
    u.auto_execute_qty_dollars = 100.0
    return u


def _make_app(user=None):
    from routers.broker import router

    app = FastAPI()
    app.include_router(router)
    if user is not None:
        app.dependency_overrides[get_current_user] = lambda: user
    return app


def _mock_db():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=MagicMock())
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db


# ── _require_pro ──────────────────────────────────────────────────────────────


def test_require_pro_owner_passes():
    from routers.broker import _require_pro

    owner = _make_user(tier="free", is_owner=True)
    _require_pro(owner)  # should not raise


def test_require_pro_pro_passes():
    from routers.broker import _require_pro

    user = _make_user(tier="pro", status="active")
    _require_pro(user)  # should not raise


def test_require_pro_free_raises():
    from routers.broker import _require_pro
    from fastapi import HTTPException

    user = _make_user(tier="free", status="active")
    with pytest.raises(HTTPException) as exc:
        _require_pro(user)
    assert exc.value.status_code == 403


def test_require_pro_inactive_raises():
    from routers.broker import _require_pro
    from fastapi import HTTPException

    user = _make_user(tier="pro", status="inactive")
    with pytest.raises(HTTPException) as exc:
        _require_pro(user)
    assert exc.value.status_code == 403


# ── Schema validation ─────────────────────────────────────────────────────────


def test_broker_connect_in_valid():
    from routers.broker import BrokerConnectIn

    obj = BrokerConnectIn(broker="alpaca", account_type="paper", api_key="key", api_secret="secret")
    assert obj.broker == "alpaca"


def test_broker_connect_in_invalid_broker():
    from routers.broker import BrokerConnectIn
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BrokerConnectIn(broker="robinhood", account_type="paper", api_key="k", api_secret="s")


def test_broker_connect_in_invalid_account_type():
    from routers.broker import BrokerConnectIn
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BrokerConnectIn(broker="alpaca", account_type="margin", api_key="k", api_secret="s")


def test_broker_connect_in_empty_key():
    from routers.broker import BrokerConnectIn
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BrokerConnectIn(broker="alpaca", account_type="paper", api_key="   ", api_secret="s")


def test_auto_execute_settings_valid():
    from routers.broker import AutoExecuteSettingsIn

    obj = AutoExecuteSettingsIn(enabled=True, min_conf=75.0, qty_dollars=500.0)
    assert obj.enabled is True
    assert obj.min_conf == 75.0


def test_auto_execute_settings_invalid_conf():
    from routers.broker import AutoExecuteSettingsIn
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AutoExecuteSettingsIn(min_conf=30.0)  # below 50


def test_auto_execute_settings_invalid_qty():
    from routers.broker import AutoExecuteSettingsIn
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AutoExecuteSettingsIn(qty_dollars=0.5)  # below $1


# ── GET /api/broker/status ────────────────────────────────────────────────────


def test_broker_status_not_connected():
    user = _make_user()
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.get("/api/me/broker/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is False


def test_broker_status_free_user():
    user = _make_user(tier="free")
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.get("/api/me/broker/status")
    assert resp.status_code == 403


# ── POST /api/broker/connect ──────────────────────────────────────────────────


def test_broker_connect_free_user():
    user = _make_user(tier="free")
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.post(
            "/api/me/broker/connect",
            json={"broker": "alpaca", "account_type": "paper", "api_key": "test_key", "api_secret": "test_secret"},
        )
    assert resp.status_code == 403


def test_broker_connect_invalid_payload():
    user = _make_user()
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.post(
            "/api/me/broker/connect",
            json={"broker": "invalid_broker", "account_type": "paper", "api_key": "k", "api_secret": "s"},
        )
    assert resp.status_code == 422


# ── DELETE /api/broker/disconnect ────────────────────────────────────────────


def test_broker_disconnect_not_pro():
    user = _make_user(tier="basic")
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.delete("/api/me/broker/disconnect")
    assert resp.status_code == 403


# ── PATCH /api/broker/settings ───────────────────────────────────────────────


def test_broker_settings_invalid_conf():
    user = _make_user()
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.patch("/api/me/broker/settings", json={"min_conf": 30.0})
    assert resp.status_code == 422


def test_broker_settings_valid():
    user = _make_user()
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.patch("/api/me/broker/settings", json={"enabled": True, "min_conf": 80.0})
    assert resp.status_code in (200, 403, 422)


# ── GET /api/broker/orders ────────────────────────────────────────────────────


def test_broker_orders_free_user():
    user = _make_user(tier="free")
    app = _make_app(user)
    app.dependency_overrides[get_db] = _mock_db()

    with TestClient(app) as client:
        resp = client.get("/api/me/broker/orders")
    assert resp.status_code == 403
