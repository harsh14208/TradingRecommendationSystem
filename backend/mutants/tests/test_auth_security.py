import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.sql.selectable import Select

from database import get_db
from models import User, EmailChangeRequest
from routers.auth import router, get_current_user

# Isolated app for auth router tests
app = FastAPI()
app.include_router(router, prefix="")


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def client(mock_db):
    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def _make_execute_result(value=None):
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


def test_account_lockout_trigger(client, mock_db):
    mock_user = User(
        id=1,
        email="lockout_test@example.com",
        password_hash="hashed_password",
        is_active=True,
        email_verified=True,
        failed_login_attempts=4,
        lockout_until=None,
    )

    # Mocking select user during login
    mock_result = _make_execute_result(mock_user)
    mock_db.execute.return_value = mock_result

    with patch("routers.auth.verify_password", return_value=False):
        resp = client.post("/api/auth/login", json={"email": "lockout_test@example.com", "password": "WrongPassword"})
        assert resp.status_code == 401

    assert mock_user.failed_login_attempts == 5
    assert mock_user.lockout_until is not None
    assert mock_db.add.call_count > 0  # verified AuthAuditLog added


def test_login_locked_out(client, mock_db):
    mock_user = User(
        id=1,
        email="lockout_test@example.com",
        password_hash="hashed_password",
        is_active=True,
        email_verified=True,
        failed_login_attempts=5,
        lockout_until=datetime.utcnow() + timedelta(minutes=15),
    )

    # Mocking select user
    mock_result = _make_execute_result(mock_user)
    mock_db.execute.return_value = mock_result

    resp = client.post("/api/auth/login", json={"email": "lockout_test@example.com", "password": "AnyPassword"})
    assert resp.status_code == 401
    assert "locked" in resp.json()["detail"].lower()


def test_admin_unlock(client, mock_db):
    mock_user = User(
        id=1,
        email="unlock_test@example.com",
        failed_login_attempts=5,
        lockout_until=datetime.utcnow() + timedelta(minutes=15),
    )
    mock_admin = User(id=2, email="admin@example.com", is_owner=True)

    # Override current user dependency
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    try:
        mock_result = _make_execute_result(mock_user)
        mock_db.execute.return_value = mock_result

        resp = client.post("/api/auth/unlock?email=unlock_test@example.com")
        assert resp.status_code == 200
        assert mock_user.failed_login_attempts == 0
        assert mock_user.lockout_until is None
    finally:
        del app.dependency_overrides[get_current_user]


def test_email_change_request(client, mock_db):
    mock_user = User(id=1, email="old@example.com", full_name="Test User", is_active=True)

    # Override current user dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        # mock no existing user with new email
        mock_result = _make_execute_result(None)
        mock_db.execute.return_value = mock_result

        with patch("services.email_svc.send_verification_email", new_callable=AsyncMock) as mock_send:
            resp = client.post("/api/auth/change-email", json={"new_email": "new@example.com"})
            assert resp.status_code == 200
            assert mock_send.call_count == 1
            assert mock_db.add.call_count > 0  # verified EmailChangeRequest added
    finally:
        del app.dependency_overrides[get_current_user]


def test_confirm_email_change(client, mock_db):
    mock_user = User(id=1, email="old@example.com", is_active=True)
    mock_request = EmailChangeRequest(
        user_id=1,
        old_email="old@example.com",
        new_email="new@example.com",
        expires_at=datetime.utcnow() + timedelta(hours=2),
    )

    # Mock select EmailChangeRequest and no conflicting new email user
    async def side_effect(query):
        if isinstance(query, Select):
            q_str = str(query)
            if "email_change_requests" in q_str:
                return _make_execute_result(mock_request)
        return _make_execute_result(None)

    mock_db.execute.side_effect = side_effect
    mock_db.get = AsyncMock(return_value=mock_user)

    resp = client.get("/api/auth/confirm-email-change?token=sometoken", follow_redirects=False)
    assert resp.status_code in (302, 303, 307)  # Redirect response
    assert mock_user.email == "new@example.com"
