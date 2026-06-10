"""TSYS-13: action audit log, risk acknowledgement, live-connect gating."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


def _make_user(**kw):
    u = User(id=1, email="t@t.com", is_owner=False, subscription_tier="pro", subscription_status="active")
    u.alpaca_key_enc = None
    u.alpaca_secret_enc = None
    u.auto_execute_broker = "alpaca"
    u.alpaca_account_type = "paper"
    u.risk_acknowledged = False
    u.risk_acknowledged_at = None
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


# ── TSYS-13c record_action ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_action_appends_audit_row():
    from models import ActionAuditLog
    from services.audit_svc import ACTION_KILL_SWITCH, record_action

    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    await record_action(db, ACTION_KILL_SWITCH, user_id=5, details={"x": 1})

    db.add.assert_called_once()
    row = db.add.call_args[0][0]
    assert isinstance(row, ActionAuditLog)
    assert row.action == ACTION_KILL_SWITCH
    assert row.user_id == 5
    db.flush.assert_awaited()


@pytest.mark.asyncio
async def test_record_action_never_raises_on_failure():
    from services.audit_svc import record_action

    db = AsyncMock()
    db.add = MagicMock(side_effect=RuntimeError("boom"))
    # Must swallow the error — auditing cannot break the audited action.
    await record_action(db, "anything", user_id=1)


# ── TSYS-13b risk acknowledgement ────────────────────────────────────────────


def test_risk_acknowledge_sets_flag():
    from routers.me import router

    user = _make_user()
    get_db_override, db = _mock_db()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = get_db_override

    resp = TestClient(app).post("/api/me/risk-acknowledge")
    assert resp.status_code == 200
    assert resp.json()["acknowledged"] is True
    assert user.risk_acknowledged is True


def test_live_broker_connect_blocked_without_acknowledgement():
    from routers.broker import router

    user = _make_user(risk_acknowledged=False)
    get_db_override, _ = _mock_db()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = get_db_override

    resp = TestClient(app).post(
        "/api/me/broker/connect",
        json={"broker": "alpaca", "api_key": "k", "api_secret": "s", "account_type": "live"},
    )
    assert resp.status_code == 403
    assert "risk acknowledgement" in resp.json()["detail"].lower()
