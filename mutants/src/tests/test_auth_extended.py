"""
Extended tests for routers/auth.py — focuses on the password reset flow.

Endpoints tested:
  - POST /api/auth/forgot-password
  - POST /api/auth/reset-password

Uses FastAPI TestClient with dependency_overrides[get_db].
Reset tokens are now DB-backed (PasswordResetToken table, SHA-256 hashed).
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import get_db
from models import PasswordResetToken, User
from routers.auth import _hash_token, router

# Isolated app for auth router tests
app = FastAPI()
app.include_router(router, prefix="")


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_execute_result(value=None):
    """Return a MagicMock whose .scalar_one_or_none() returns value."""
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


@pytest.fixture
def mock_db():
    """An AsyncMock that simulates an async SQLAlchemy session."""
    db = AsyncMock()
    db.execute.return_value = _make_execute_result(None)
    return db


@pytest.fixture
def client(mock_db):
    """Override get_db with the mock session."""

    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def _mock_user(email="reset@example.com", password_hash="old_hash", user_id=42):
    return User(
        id=user_id,
        email=email,
        password_hash=password_hash,
        is_owner=False,
        subscription_tier="free",
        is_active=True,
        email_verified=True,
    )


def _mock_reset_row(token: str, email: str, expired: bool = False, used: bool = False):
    """Return a PasswordResetToken mock with correct hash and expiry."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    row = MagicMock(spec=PasswordResetToken)
    row.token_hash = _hash_token(token)
    row.email = email
    row.expires_at = now - timedelta(seconds=10) if expired else now + timedelta(hours=1)
    row.used = used
    return row


# ── forgot-password tests ─────────────────────────────────────────────────────


class TestForgotPassword:
    def test_forgot_password_known_email_returns_200(self, client, mock_db):
        user = _mock_user()
        mock_db.execute.return_value = _make_execute_result(user)

        with (
            patch("services.email_svc.send_password_reset", new=AsyncMock()),
            patch("routers.auth._secrets.token_urlsafe", return_value="TEST_TOKEN_ABC"),
        ):
            resp = client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})

        assert resp.status_code == 200
        assert "reset link" in resp.json()["message"].lower()

    def test_forgot_password_unknown_email_returns_200(self, client, mock_db):
        """Unknown email still returns 200 (prevents email enumeration)."""
        mock_db.execute.return_value = _make_execute_result(None)

        resp = client.post("/api/auth/forgot-password", json={"email": "unknown@example.com"})
        assert resp.status_code == 200
        assert "message" in resp.json()

    def test_forgot_password_adds_token_to_db(self, client, mock_db):
        """After a valid forgot-password call, db.add is called with a PasswordResetToken."""
        user = _mock_user()
        mock_db.execute.return_value = _make_execute_result(user)

        fixed_token = "FIXED_TOKEN_XYZ"
        with (
            patch("services.email_svc.send_password_reset", new=AsyncMock()),
            patch("routers.auth._secrets.token_urlsafe", return_value=fixed_token),
        ):
            client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})

        assert mock_db.add.called
        added = mock_db.add.call_args[0][0]
        assert isinstance(added, PasswordResetToken)
        assert added.token_hash == _hash_token(fixed_token)
        assert added.email == "reset@example.com"


# ── reset-password tests ───────────────────────────────────────────────────────


class TestResetPassword:
    def _seed_token(
        self, mock_db, token: str, email: str, expired: bool = False, used: bool = False, user: User | None = None
    ):
        """Configure mock_db.execute to return a valid PasswordResetToken for this token,
        then a user on the second execute call."""
        row = _mock_reset_row(token, email, expired=expired, used=used)
        if expired or used:
            mock_db.execute.return_value = _make_execute_result(None)
        else:
            mock_db.execute.side_effect = [
                _make_execute_result(row),  # token lookup
                _make_execute_result(user or _mock_user(email=email)),  # user lookup
                MagicMock(),  # RefreshToken revoke UPDATE
            ]

    def test_valid_token_resets_password(self, client, mock_db):
        token = "VALID_TOKEN_001"
        self._seed_token(mock_db, token, "reset@example.com")

        with patch("routers.auth.hash_password", return_value="new_hash"):
            resp = client.post(
                "/api/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "NewStr0ngPass!",
                },
            )

        assert resp.status_code == 200
        assert "successfully" in resp.json()["message"].lower()

    def test_valid_token_revokes_refresh_tokens(self, client, mock_db):
        token = "VALID_TOKEN_002"
        self._seed_token(mock_db, token, "reset@example.com")

        with patch("routers.auth.hash_password", return_value="new_hash"):
            resp = client.post(
                "/api/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "NewStr0ngPass!",
                },
            )

        assert resp.status_code == 200
        # db.execute called for: token lookup, user lookup, refresh token revoke
        assert mock_db.execute.call_count >= 2

    def test_token_marked_used_after_reset(self, client, mock_db):
        """row.used is set to True after a successful reset."""
        token = "ONE_TIME_TOKEN"
        row = _mock_reset_row(token, "reset@example.com")
        mock_db.execute.side_effect = [
            _make_execute_result(row),
            _make_execute_result(_mock_user()),
            MagicMock(),  # RefreshToken revoke UPDATE
        ]

        with patch("routers.auth.hash_password", return_value="new_hash"):
            client.post(
                "/api/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "NewStr0ngPass!",
                },
            )

        assert row.used is True

    def test_invalid_token_returns_400(self, client, mock_db):
        """Non-existent token → 400."""
        mock_db.execute.return_value = _make_execute_result(None)

        resp = client.post(
            "/api/auth/reset-password",
            json={
                "token": "DOES_NOT_EXIST",
                "new_password": "SomePassword1!",
            },
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"].lower()
        assert "invalid" in detail or "expired" in detail

    def test_expired_token_returns_400(self, client, mock_db):
        """Expired token is filtered by DB query → 400."""
        # DB returns None because expires_at condition filters it out
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        resp = client.post(
            "/api/auth/reset-password",
            json={
                "token": "EXPIRED_TOKEN",
                "new_password": "SomePassword1!",
            },
        )
        assert resp.status_code == 400

    def test_password_too_short_returns_400(self, client, mock_db):
        token = "SHORT_PW_TOKEN"
        row = _mock_reset_row(token, "reset@example.com")
        mock_db.execute.side_effect = [
            _make_execute_result(row),
            _make_execute_result(_mock_user()),
        ]

        resp = client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "new_password": "short",
            },
        )
        assert resp.status_code == 400
        assert "8" in resp.json()["detail"]

    def test_user_not_found_returns_400(self, client, mock_db):
        token = "NO_USER_TOKEN"
        row = _mock_reset_row(token, "ghost@example.com")
        mock_db.execute.side_effect = [
            _make_execute_result(row),
            _make_execute_result(None),  # user not found
        ]

        resp = client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "new_password": "ValidPass123!",
            },
        )
        assert resp.status_code == 400

    def test_second_use_of_consumed_token_fails(self, client, mock_db):
        """After a successful reset, reusing the same token fails (row.used=True filtered by DB)."""
        token = "REUSE_TOKEN"
        mock_db.execute.side_effect = [
            _make_execute_result(_mock_reset_row(token, "reset@example.com")),
            _make_execute_result(_mock_user()),
            MagicMock(),  # RefreshToken revoke UPDATE
        ]

        with patch("routers.auth.hash_password", return_value="new_hash"):
            first = client.post(
                "/api/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "ValidPass123!",
                },
            )
        assert first.status_code == 200

        # Second use — DB now returns None (row.used=True is filtered out)
        mock_db.execute.side_effect = None
        mock_db.execute.return_value = _make_execute_result(None)
        second = client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "new_password": "ValidPass123!",
            },
        )
        assert second.status_code == 400


# ── Additional auth router coverage ──────────────────────────────────────────


class TestAuthMiscEndpoints:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def client(self, mock_db):
        async def _override_db():
            yield mock_db

        app.dependency_overrides[get_db] = _override_db
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c
        app.dependency_overrides.clear()

    def test_register_short_password_422(self, client, mock_db):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result

        resp = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "password": "short",
                "full_name": "New User",
            },
        )
        assert resp.status_code == 422

    def test_register_name_too_long_422(self, client, mock_db):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result

        resp = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "password": "ValidPass123!",
                "full_name": "A" * 61,
            },
        )
        assert resp.status_code == 422

    def test_login_inactive_account_403(self, client, mock_db):
        mock_user = _mock_user()
        mock_user.is_active = False
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result

        with patch("routers.auth.verify_password", return_value=True):
            resp = client.post(
                "/api/auth/login",
                json={
                    "email": "trader@example.com",
                    "password": "correct_pass",
                },
            )
        assert resp.status_code == 403

    def test_login_unverified_email_403(self, client, mock_db):
        mock_user = _mock_user()
        mock_user.email_verified = False
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result

        with patch("routers.auth.verify_password", return_value=True):
            resp = client.post(
                "/api/auth/login",
                json={
                    "email": "trader@example.com",
                    "password": "correct_pass",
                },
            )
        assert resp.status_code == 403
        assert resp.json()["detail"]["code"] == "email_unverified"

    def test_signal_prefs_update_valid(self, client, mock_db):
        from services.auth_svc import get_current_user

        mock_user = _mock_user()
        mock_user.min_confidence_override = None
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_db.commit = AsyncMock()

        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": 65.0})
        assert resp.status_code == 200

    def test_signal_prefs_out_of_range_400(self, client, mock_db):
        from services.auth_svc import get_current_user

        mock_user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": 105.0})
        assert resp.status_code == 400

    def test_signal_prefs_null_reverts_to_global(self, client, mock_db):
        from services.auth_svc import get_current_user

        mock_user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_db.commit = AsyncMock()

        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": None})
        assert resp.status_code == 200
        assert "global" in resp.json()["message"].lower()
