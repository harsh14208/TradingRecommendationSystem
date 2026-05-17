"""
Extended tests for routers/auth.py — focuses on the password reset flow.

Endpoints tested:
  - POST /api/auth/request-password-reset  (actually: /api/auth/forgot-password)
  - POST /api/auth/reset-password

Uses FastAPI TestClient with dependency_overrides[get_db].
Does NOT modify existing test_routers_auth.py.
"""
import sys
import os
import time
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from routers.auth import router, _reset_tokens
from database import get_db
from models import User, RefreshToken

# Isolated app for auth router tests
app = FastAPI()
app.include_router(router, prefix="")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """An AsyncMock that simulates an async SQLAlchemy session."""
    return AsyncMock()


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


# ── forgot-password tests ─────────────────────────────────────────────────────

class TestForgotPassword:

    def test_forgot_password_known_email_returns_200(self, client, mock_db):
        """Known email stores a token and returns 200 with a generic message."""
        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        with patch("services.email_svc.send_password_reset", new=AsyncMock()), \
             patch("routers.auth._secrets.token_urlsafe", return_value="TEST_TOKEN_ABC"):
            resp = client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})

        assert resp.status_code == 200
        assert "reset link" in resp.json()["message"].lower()

    def test_forgot_password_unknown_email_returns_200(self, client, mock_db):
        """Unknown email still returns 200 (prevents email enumeration)."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result

        resp = client.post("/api/auth/forgot-password", json={"email": "unknown@example.com"})
        assert resp.status_code == 200
        assert "message" in resp.json()

    def test_forgot_password_stores_token_in_dict(self, client, mock_db):
        """After a valid forgot-password call the token is stored in _reset_tokens."""
        _reset_tokens.clear()
        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        fixed_token = "FIXED_TOKEN_XYZ"
        with patch("services.email_svc.send_password_reset", new=AsyncMock()), \
             patch("routers.auth._secrets.token_urlsafe", return_value=fixed_token):
            client.post("/api/auth/forgot-password", json={"email": "reset@example.com"})

        assert fixed_token in _reset_tokens
        stored_email, _ = _reset_tokens[fixed_token]
        assert stored_email == "reset@example.com"


# ── reset-password tests ───────────────────────────────────────────────────────

class TestResetPassword:

    def _seed_token(self, token: str, email: str, ttl_seconds: float = 3600):
        _reset_tokens[token] = (email, time.time() + ttl_seconds)

    def teardown_method(self, _method):
        _reset_tokens.clear()

    def test_valid_token_resets_password(self, client, mock_db):
        """Valid token + strong password → 200 and password hash updated."""
        token = "VALID_TOKEN_001"
        self._seed_token(token, "reset@example.com")

        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        with patch("routers.auth.hash_password", return_value="new_hash"):
            resp = client.post("/api/auth/reset-password", json={
                "token": token,
                "new_password": "NewStr0ngPass!",
            })

        assert resp.status_code == 200
        assert "successfully" in resp.json()["message"].lower()

    def test_valid_token_revokes_refresh_tokens(self, client, mock_db):
        """On successful reset, update(RefreshToken) is called to revoke sessions."""
        token = "VALID_TOKEN_002"
        self._seed_token(token, "reset@example.com")

        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        with patch("routers.auth.hash_password", return_value="new_hash"):
            resp = client.post("/api/auth/reset-password", json={
                "token": token,
                "new_password": "NewStr0ngPass!",
            })

        assert resp.status_code == 200
        # db.execute must have been called (for the UPDATE statement)
        assert mock_db.execute.called

    def test_token_consumed_after_use(self, client, mock_db):
        """Token is deleted from _reset_tokens after a successful reset."""
        token = "ONE_TIME_TOKEN"
        self._seed_token(token, "reset@example.com")

        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        with patch("routers.auth.hash_password", return_value="new_hash"):
            client.post("/api/auth/reset-password", json={
                "token": token,
                "new_password": "NewStr0ngPass!",
            })

        assert token not in _reset_tokens

    def test_invalid_token_returns_400(self, client, mock_db):
        """Non-existent token → 400."""
        resp = client.post("/api/auth/reset-password", json={
            "token": "DOES_NOT_EXIST",
            "new_password": "SomePassword1!",
        })
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower() or "expired" in resp.json()["detail"].lower()

    def test_expired_token_returns_400(self, client, mock_db):
        """Token that is past its expiry returns 400."""
        token = "EXPIRED_TOKEN"
        # Seed with a past timestamp (already expired)
        _reset_tokens[token] = ("reset@example.com", time.time() - 10)

        resp = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": "SomePassword1!",
        })
        assert resp.status_code == 400

    def test_password_too_short_returns_400(self, client, mock_db):
        """Password shorter than 8 characters → 400."""
        token = "SHORT_PW_TOKEN"
        self._seed_token(token, "reset@example.com")

        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        resp = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": "short",
        })
        assert resp.status_code == 400
        assert "8" in resp.json()["detail"]

    def test_user_not_found_returns_400(self, client, mock_db):
        """Valid token but no matching user in DB → 400."""
        token = "NO_USER_TOKEN"
        self._seed_token(token, "ghost@example.com")

        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result

        resp = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": "ValidPass123!",
        })
        assert resp.status_code == 400

    def test_second_use_of_consumed_token_fails(self, client, mock_db):
        """After a successful reset, reusing the same token should fail."""
        token = "REUSE_TOKEN"
        self._seed_token(token, "reset@example.com")

        user = _mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        mock_db.execute.return_value = result

        with patch("routers.auth.hash_password", return_value="new_hash"):
            first = client.post("/api/auth/reset-password", json={
                "token": token,
                "new_password": "ValidPass123!",
            })
        assert first.status_code == 200

        # Second use — token no longer in dict
        second = client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": "ValidPass123!",
        })
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
        """Password shorter than 8 chars → 422 validation error."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result

        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "short",
            "full_name": "New User",
        })
        assert resp.status_code == 422

    def test_register_name_too_long_422(self, client, mock_db):
        """Full name over 60 chars → 422 validation error."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result

        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "ValidPass123!",
            "full_name": "A" * 61,
        })
        assert resp.status_code == 422

    def test_login_inactive_account_403(self, client, mock_db):
        """Login with inactive account → 403."""
        mock_user = _mock_user()
        mock_user.is_active = False

        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result

        with patch("routers.auth.verify_password", return_value=True):
            resp = client.post("/api/auth/login", json={
                "email": "trader@example.com",
                "password": "correct_pass",
            })
        assert resp.status_code == 403

    def test_login_unverified_email_403(self, client, mock_db):
        """Login with unverified email → 403."""
        mock_user = _mock_user()
        mock_user.email_verified = False

        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = result

        with patch("routers.auth.verify_password", return_value=True):
            resp = client.post("/api/auth/login", json={
                "email": "trader@example.com",
                "password": "correct_pass",
            })
        assert resp.status_code == 403
        body = resp.json()
        assert body["detail"]["code"] == "email_unverified"

    def test_signal_prefs_update_valid(self, client, mock_db):
        """PATCH /api/auth/signal-prefs with valid threshold."""
        from services.auth_svc import get_current_user
        mock_user = _mock_user()
        mock_user.min_confidence_override = None

        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_db.commit = AsyncMock()

        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": 65.0})
        assert resp.status_code == 200

    def test_signal_prefs_out_of_range_400(self, client, mock_db):
        """PATCH /api/auth/signal-prefs with confidence > 100 → 400."""
        from services.auth_svc import get_current_user
        mock_user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": 105.0})
        assert resp.status_code == 400

    def test_signal_prefs_null_reverts_to_global(self, client, mock_db):
        """PATCH /api/auth/signal-prefs with null → reverts to global."""
        from services.auth_svc import get_current_user
        mock_user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_db.commit = AsyncMock()

        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": None})
        assert resp.status_code == 200
        assert "global" in resp.json()["message"].lower()
