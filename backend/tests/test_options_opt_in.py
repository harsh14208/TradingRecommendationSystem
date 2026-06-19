"""Tests for options execution opt-in and risk acknowledgement endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


def _make_user(**kw):
    u = User(
        id=1,
        email="t@t.com",
        is_owner=False,
        subscription_tier="pro",
        subscription_status="active",
        options_mode="signal",
        options_risk_acknowledged=False,
        options_risk_acknowledged_at=None,
        risk_acknowledged=False,
    )
    u.alpaca_key_enc = None
    u.alpaca_secret_enc = None
    u.auto_execute_broker = "alpaca"
    u.alpaca_account_type = "paper"
    for k, v in kw.items():
        setattr(u, k, v)
    return u


def _mock_db():
    db = MagicMock()
    db.execute = AsyncMock(return_value=MagicMock())
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    db.merge = AsyncMock(side_effect=lambda u: u)

    async def _get_db():
        yield db

    return _get_db, db


def _app(user):
    from routers.me import router

    get_db_override, _ = _mock_db()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = get_db_override
    return app


def test_get_options_settings():
    user = _make_user(options_capital=50_000.0)
    resp = TestClient(_app(user)).get("/api/me/options/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["options_mode"] == "signal"
    assert data["options_capital"] == 50_000.0
    assert data["options_risk_acknowledged"] is False


def test_options_risk_acknowledge_sets_flag():
    user = _make_user()
    resp = TestClient(_app(user)).post("/api/me/options/risk-acknowledge")
    assert resp.status_code == 200
    assert resp.json()["acknowledged"] is True
    assert user.options_risk_acknowledged is True


def test_paper_mode_blocked_without_ack():
    user = _make_user(options_risk_acknowledged=False)
    resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "paper"})
    assert resp.status_code == 403
    assert "options risk acknowledgement" in resp.json()["detail"].lower()


def test_paper_mode_allowed_after_ack():
    user = _make_user(options_risk_acknowledged=True)
    resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "paper"})
    assert resp.status_code == 200
    assert resp.json()["options_mode"] == "paper"


def test_live_mode_blocked_without_trading_ack():
    user = _make_user(options_risk_acknowledged=True, risk_acknowledged=False)
    resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "live"})
    assert resp.status_code == 403
    assert "trading risk acknowledgement" in resp.json()["detail"].lower()


def test_live_mode_blocked_without_alpaca_credentials():
    user = _make_user(options_risk_acknowledged=True, risk_acknowledged=True, alpaca_key_enc=None)
    resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "live"})
    assert resp.status_code == 400


def test_live_mode_blocked_when_account_not_options_approved():
    user = _make_user(
        options_risk_acknowledged=True,
        risk_acknowledged=True,
        alpaca_key_enc="enc",
        alpaca_secret_enc="enc",
        alpaca_account_type="live",
    )
    with patch(
        "services.alpaca_rest.get_account",
        new_callable=AsyncMock,
        return_value={"option_approved_level": "2"},
    ):
        resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "live"})
    assert resp.status_code == 403
    assert "approval level" in resp.json()["detail"].lower()


def test_live_mode_allowed_with_options_approval():
    user = _make_user(
        options_risk_acknowledged=True,
        risk_acknowledged=True,
        alpaca_key_enc="enc",
        alpaca_secret_enc="enc",
        alpaca_account_type="live",
    )
    with patch(
        "services.alpaca_rest.get_account",
        new_callable=AsyncMock,
        return_value={"option_approved_level": "3"},
    ):
        resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "live"})
    assert resp.status_code == 200
    assert resp.json()["options_mode"] == "live"


def test_invalid_options_mode_rejected():
    user = _make_user(options_risk_acknowledged=True)
    resp = TestClient(_app(user)).put("/api/me/options/settings", json={"options_mode": "invalid"})
    assert resp.status_code == 400
