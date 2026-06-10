"""
Test file targeting uncovered code in:
- routers/auth.py
- routers/billing.py
- routers/broker.py
- services/dark_pool.py
- services/ibkr_rest.py
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.sql.selectable import Select

from database import get_db
from models import (
    BrokerOrder,
    EmailChangeRequest,
    RefreshToken,
    User,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _make_execute_result(value=None):
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


def _make_user(**kw):
    defaults = dict(
        id=1,
        email="t@t.com",
        is_owner=False,
        subscription_tier="pro",
        subscription_status="active",
        full_name="Test User",
        alpaca_key_enc=None,
        alpaca_secret_enc=None,
        auto_execute_broker="alpaca",
        alpaca_account_type="paper",
        auto_execute_min_conf=75.0,
        auto_execute_qty_dollars=100.0,
        stripe_customer_id=None,
        stripe_subscription_id=None,
        referral_rewarded=False,
        referred_by=None,
        risk_acknowledged=False,
    )
    defaults.update(kw)
    u = User(**{k: v for k, v in defaults.items() if k in {"id", "email", "is_owner", "subscription_tier", "subscription_status", "full_name"}})
    for k, v in defaults.items():
        setattr(u, k, v)
    return u


def _mock_db():
    db = MagicMock()
    db.execute = AsyncMock(return_value=MagicMock())
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.merge = AsyncMock(side_effect=lambda x: x)
    db.add = MagicMock()
    db.delete = AsyncMock()

    async def _get_db():
        yield db

    return _get_db, db


# ═══════════════════════════════════════════════════════════════════════════════
# routers/auth.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthRouter:
    @pytest.fixture
    def app(self):
        from routers.auth import router, get_current_user
        app = FastAPI()
        app.include_router(router, prefix="")
        return app, get_current_user

    @pytest.fixture
    def client(self, app):
        app_inst, _ = app
        db = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with TestClient(app_inst, raise_server_exceptions=False) as c:
            yield c
        app_inst.dependency_overrides.clear()

    # ── validators ───────────────────────────────────────────────────────────

    def test_register_email_too_long(self, app, client):
        long_email = "a" * 250 + "@x.com"
        resp = client.post("/api/auth/register", json={"email": long_email, "password": "password123"})
        assert resp.status_code == 422

    def test_register_full_name_too_long(self, app, client):
        long_name = "x" * 61
        resp = client.post("/api/auth/register", json={"email": "new@example.com", "password": "password123", "full_name": long_name})
        assert resp.status_code == 422

    def test_change_email_invalid_email(self, app, client):
        app_inst, get_current_user = app
        app_inst.dependency_overrides[get_current_user] = lambda: _make_user()
        resp = client.post("/api/auth/change-email", json={"new_email": "not-an-email"})
        assert resp.status_code == 422
        app_inst.dependency_overrides.pop(get_current_user, None)

    def test_update_me_validators(self, app, client):
        app_inst, get_current_user = app
        app_inst.dependency_overrides[get_current_user] = lambda: _make_user()
        # full_name too long
        resp = client.patch("/api/auth/me", json={"full_name": "x" * 61})
        assert resp.status_code == 422
        # auto_execute_min_conf out of range
        resp = client.patch("/api/auth/me", json={"auto_execute_min_conf": 120.0})
        assert resp.status_code == 422
        # invalid broker
        resp = client.patch("/api/auth/me", json={"auto_execute_broker": "robinhood"})
        assert resp.status_code == 422
        app_inst.dependency_overrides.pop(get_current_user, None)

    # ── register with referrer / auto-verified branches ──────────────────────

    def test_register_with_invalid_referrer(self, app, client):
        app_inst, _ = app
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.smtp_host = "smtp.example.com"
            s.smtp_user = "user"
            s.app_url = "http://localhost"
            s.owner_email = "owner@example.com"
            s.refresh_token_expire_days = 7
            mock_settings.return_value = s
            with patch("routers.auth.send_verification_email", new_callable=AsyncMock):
                resp = client.post("/api/auth/register?ref=9999", json={"email": "ref@example.com", "password": "password123"})
        assert resp.status_code == 201
        assert "check your email" in resp.json()["message"].lower()
        app_inst.dependency_overrides.pop(get_db, None)

    def test_register_auto_verified_no_smtp(self, app, client):
        app_inst, _ = app
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.smtp_host = None
            s.smtp_user = None
            s.app_url = "http://localhost"
            s.owner_email = ""
            s.refresh_token_expire_days = 7
            mock_settings.return_value = s
            with patch("routers.auth.send_welcome", new_callable=AsyncMock):
                resp = client.post("/api/auth/register", json={"email": "auto@example.com", "password": "password123"})
        assert resp.status_code == 201
        assert "access_token" in resp.json()
        app_inst.dependency_overrides.pop(get_db, None)

    # ── refresh endpoints ────────────────────────────────────────────────────

    def test_refresh_token_returns_501(self, app, client):
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 501

    def test_refresh_cookie_invalid_token(self, app, client):
        resp = client.post("/api/auth/refresh-cookie")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "No refresh token."

    def test_refresh_cookie_expired_token(self, app, client):
        app_inst, _ = app
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        client.cookies.set("st_refresh", "bad_token")
        resp = client.post("/api/auth/refresh-cookie")
        assert resp.status_code == 401
        app_inst.dependency_overrides.pop(get_db, None)

    def test_refresh_cookie_user_inactive(self, app, client):
        app_inst, _ = app
        token_row = MagicMock()
        token_row.user_id = 1
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(token_row))
        db.get = AsyncMock(return_value=None)

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        client.cookies.set("st_refresh", "some_token")
        resp = client.post("/api/auth/refresh-cookie")
        assert resp.status_code == 401
        app_inst.dependency_overrides.pop(get_db, None)

    # ── delete account ───────────────────────────────────────────────────────

    def test_delete_account(self, app, client):
        app_inst, get_current_user = app
        user = _make_user(stripe_subscription_id="sub_123")
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock())
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.app_url = "http://localhost"
            mock_settings.return_value = s
            with patch("stripe.Subscription.modify") as mock_stripe_mod:
                resp = client.delete("/api/auth/me")
        assert resp.status_code == 200
        assert user.is_active is False
        assert "deleted" in user.email
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── update me ────────────────────────────────────────────────────────────

    def test_update_me_fields(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.patch("/api/auth/me", json={"full_name": "", "auto_execute": True, "auto_execute_min_conf": 80.0, "auto_execute_broker": "ibkr"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["auto_execute"] is True
        assert data["auto_execute_min_conf"] == 80.0
        assert data["auto_execute_broker"] == "ibkr"
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── telegram ─────────────────────────────────────────────────────────────

    def test_telegram_link_code(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        user.telegram_link_code = "old_code"
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.generate_link_code", return_value="new_code"):
            resp = client.post("/api/auth/telegram-link-code")
        assert resp.status_code == 200
        assert resp.json()["link_code"] == "new_code"
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_telegram_unlink(self, app, client):
        app_inst, get_current_user = app
        user = _make_user(telegram_chat_id="12345")
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.delete("/api/auth/telegram-unlink")
        assert resp.status_code == 200
        assert user.telegram_chat_id is None
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── referral ─────────────────────────────────────────────────────────────

    def test_referral_info(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()

        def _make_result(val):
            r = MagicMock()
            r.scalar.return_value = val
            return r

        db.execute = AsyncMock(side_effect=[_make_result(5), _make_result(0)])

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.app_url = "https://app.example.com"
            mock_settings.return_value = s
            resp = client.get("/api/auth/referral")
        assert resp.status_code == 200
        data = resp.json()
        assert data["referrals_total"] == 5
        assert data["rewards_pending"] == 5
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── signal prefs ─────────────────────────────────────────────────────────

    def test_signal_prefs_update(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": 85.0})
        assert resp.status_code == 200
        assert "85%" in resp.json()["message"]
        # reset to null
        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": None})
        assert resp.status_code == 200
        assert "global" in resp.json()["message"].lower()
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_signal_prefs_invalid(self, app, client):
        app_inst, get_current_user = app
        app_inst.dependency_overrides[get_current_user] = lambda: _make_user()
        db = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.patch("/api/auth/signal-prefs", json={"min_confidence": 150.0})
        assert resp.status_code == 400
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── verify email ─────────────────────────────────────────────────────────

    def test_verify_email_success(self, app, client):
        app_inst, _ = app
        user = _make_user(email="unverified@example.com", email_verified=False, email_verify_token="tok123")
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(user))
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.send_welcome", new_callable=AsyncMock):
            with patch("routers.auth.get_settings") as mock_settings:
                s = MagicMock()
                s.refresh_token_expire_days = 7
                s.app_url = "http://localhost"
                mock_settings.return_value = s
                resp = client.get("/api/auth/verify-email?token=tok123")
        assert resp.status_code == 200
        assert user.email_verified is True
        app_inst.dependency_overrides.pop(get_db, None)

    def test_verify_email_already_verified(self, app, client):
        app_inst, _ = app
        user = _make_user(email_verified=True)
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(user))

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.get("/api/auth/verify-email?token=tok123")
        assert resp.status_code == 400
        app_inst.dependency_overrides.pop(get_db, None)

    # ── integrations ─────────────────────────────────────────────────────────

    def test_integrations_discord(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        # valid discord webhook
        resp = client.patch("/api/auth/integrations", json={"discord_webhook_url": "https://discord.com/api/webhooks/123/abc"})
        assert resp.status_code == 200
        # invalid discord webhook
        resp = client.patch("/api/auth/integrations", json={"discord_webhook_url": "https://example.com/hook"})
        assert resp.status_code == 400
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_integrations_webhook_url_ssrf(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        # localhost blocked
        resp = client.patch("/api/auth/integrations", json={"webhook_url": "https://localhost:8080/hook"})
        assert resp.status_code == 400
        # private IP blocked
        resp = client.patch("/api/auth/integrations", json={"webhook_url": "https://192.168.1.1/hook"})
        assert resp.status_code == 400
        # loopback blocked
        resp = client.patch("/api/auth/integrations", json={"webhook_url": "https://127.0.0.1/hook"})
        assert resp.status_code == 400
        # valid public url
        resp = client.patch("/api/auth/integrations", json={"webhook_url": "https://example.com/hook"})
        assert resp.status_code == 200
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── resend verification ──────────────────────────────────────────────────

    def test_resend_verification(self, app, client):
        app_inst, _ = app
        user = _make_user(email="unv@example.com", email_verified=False, email_verify_token="old_tok")
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(user))
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.send_verification_email", new_callable=AsyncMock):
            with patch("routers.auth.get_settings") as mock_settings:
                s = MagicMock()
                s.app_url = "http://localhost"
                mock_settings.return_value = s
                resp = client.post("/api/auth/resend-verification", json={"email": "unv@example.com"})
        assert resp.status_code == 200
        app_inst.dependency_overrides.pop(get_db, None)

    def test_resend_verification_already_verified(self, app, client):
        app_inst, _ = app
        user = _make_user(email_verified=True)
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(user))

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/resend-verification", json={"email": "ver@example.com"})
        assert resp.status_code == 200
        app_inst.dependency_overrides.pop(get_db, None)

    # ── sessions ─────────────────────────────────────────────────────────────

    def test_list_sessions(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        token = RefreshToken(
            id=1,
            user_id=1,
            token_hash=hashlib.sha256(b"cookie_val").hexdigest(),
            revoked=False,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7),
        )
        db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [token]
        db.execute = AsyncMock(return_value=result)

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        client.cookies.set("st_refresh", "cookie_val")
        resp = client.get("/api/auth/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["is_current"] is True
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_revoke_session(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        token = RefreshToken(id=1, user_id=1, revoked=False)
        db = AsyncMock()
        db.get = AsyncMock(return_value=token)
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/sessions/revoke/1")
        assert resp.status_code == 200
        assert token.revoked is True
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_revoke_session_not_found(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.get = AsyncMock(return_value=None)

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/sessions/revoke/99")
        assert resp.status_code == 404
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_revoke_other_sessions(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock())
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        client.cookies.set("st_refresh", "my_token")
        resp = client.post("/api/auth/sessions/revoke-others")
        assert resp.status_code == 200
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_revoke_other_sessions_no_cookie(self, app, client):
        app_inst, get_current_user = app
        user = _make_user()
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/sessions/revoke-others")
        assert resp.status_code == 400
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── change email ─────────────────────────────────────────────────────────

    def test_change_email_same_email(self, app, client):
        app_inst, get_current_user = app
        user = _make_user(email="same@example.com")
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/change-email", json={"new_email": "same@example.com"})
        assert resp.status_code == 400
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_change_email_already_registered(self, app, client):
        app_inst, get_current_user = app
        user = _make_user(email="old@example.com")
        app_inst.dependency_overrides[get_current_user] = lambda: user
        existing = _make_user(email="new@example.com")
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(existing))

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/change-email", json={"new_email": "new@example.com"})
        assert resp.status_code == 400
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    def test_change_email_send_exception(self, app, client):
        app_inst, get_current_user = app
        user = _make_user(email="old@example.com")
        app_inst.dependency_overrides[get_current_user] = lambda: user
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))
        db.commit = AsyncMock()

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.send_verification_email", side_effect=Exception("SMTP down")):
            with patch("routers.auth.get_settings") as mock_settings:
                s = MagicMock()
                s.app_url = "http://localhost"
                mock_settings.return_value = s
                resp = client.post("/api/auth/change-email", json={"new_email": "new@example.com"})
        assert resp.status_code == 200
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)

    # ── confirm email change ─────────────────────────────────────────────────

    def test_confirm_email_change_invalid_token(self, app, client):
        app_inst, _ = app
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.app_url = "http://localhost"
            mock_settings.return_value = s
            resp = client.get("/api/auth/confirm-email-change?token=bad", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert "invalid" in resp.headers["location"]
        app_inst.dependency_overrides.pop(get_db, None)

    def test_confirm_email_change_user_not_found(self, app, client):
        app_inst, _ = app
        req = EmailChangeRequest(user_id=99, old_email="old@example.com", new_email="new@example.com")
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(req))
        db.get = AsyncMock(return_value=None)

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.app_url = "http://localhost"
            mock_settings.return_value = s
            resp = client.get("/api/auth/confirm-email-change?token=tok", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert "user_not_found" in resp.headers["location"]
        app_inst.dependency_overrides.pop(get_db, None)

    def test_confirm_email_change_email_taken(self, app, client):
        app_inst, _ = app
        req = EmailChangeRequest(user_id=1, old_email="old@example.com", new_email="new@example.com")
        user = _make_user(id=1)
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(req))
        db.get = AsyncMock(return_value=user)

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        with patch("routers.auth.get_settings") as mock_settings:
            s = MagicMock()
            s.app_url = "http://localhost"
            mock_settings.return_value = s
            resp = client.get("/api/auth/confirm-email-change?token=tok", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert "email_already_registered" in resp.headers["location"]
        app_inst.dependency_overrides.pop(get_db, None)

    # ── admin unlock ─────────────────────────────────────────────────────────

    def test_admin_unlock_forbidden(self, app, client):
        app_inst, get_current_user = app
        app_inst.dependency_overrides[get_current_user] = lambda: _make_user(is_owner=False)
        resp = client.post("/api/auth/unlock?email=target@example.com")
        assert resp.status_code == 403
        app_inst.dependency_overrides.pop(get_current_user, None)

    def test_admin_unlock_user_not_found(self, app, client):
        app_inst, get_current_user = app
        app_inst.dependency_overrides[get_current_user] = lambda: _make_user(is_owner=True)
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))

        async def _override_db():
            yield db

        app_inst.dependency_overrides[get_db] = _override_db
        resp = client.post("/api/auth/unlock?email=missing@example.com")
        assert resp.status_code == 404
        app_inst.dependency_overrides.pop(get_current_user, None)
        app_inst.dependency_overrides.pop(get_db, None)


# ═══════════════════════════════════════════════════════════════════════════════
# routers/billing.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestBillingRouter:
    @pytest.fixture
    def app(self):
        from routers.billing import router
        from services.auth_svc import get_current_user
        app = FastAPI()
        app.include_router(router)
        return app, get_current_user

    def _make_app(self, app, tier="free", status="active", stripe_id=None, sub_id=None):
        app_inst, get_current_user = app
        user = _make_user(tier=tier, status=status, stripe_id=stripe_id)
        user.stripe_subscription_id = sub_id
        app_inst.dependency_overrides[get_current_user] = lambda: user
        return app_inst

    def test_status_with_stripe_enrichment(self, app):
        app_inst = self._make_app(app, tier="pro", status="active", stripe_id="cus_123", sub_id="sub_123")
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("routers.billing.get_settings") as mock_settings:
            s = MagicMock()
            s.stripe_secret_key = "sk_test"
            mock_settings.return_value = s
            mock_stripe = MagicMock()
            mock_sub = {
                "cancel_at_period_end": True,
                "current_period_end": 1774880000,
                "default_payment_method": {
                    "card": {"brand": "visa", "last4": "4242", "exp_month": 12, "exp_year": 2030}
                },
            }
            mock_stripe.Subscription.retrieve.return_value = mock_sub
            with patch("routers.billing._stripe", return_value=mock_stripe):
                with TestClient(app_inst) as client:
                    resp = client.get("/api/billing/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["cancel_at_period_end"] is True
        assert data["payment_method"]["brand"] == "visa"
        assert data["cancellation_date"] is not None

    def test_status_stripe_exception(self, app):
        app_inst = self._make_app(app, tier="pro", status="active", stripe_id="cus_123", sub_id="sub_123")
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("routers.billing.get_settings") as mock_settings:
            s = MagicMock()
            s.stripe_secret_key = "sk_test"
            mock_settings.return_value = s
            mock_stripe = MagicMock()
            mock_stripe.Subscription.retrieve.side_effect = Exception("stripe down")
            with patch("routers.billing._stripe", return_value=mock_stripe):
                with TestClient(app_inst) as client:
                    resp = client.get("/api/billing/status")
        assert resp.status_code == 200

    def test_status_past_due(self, app):
        from datetime import datetime
        user = _make_user(tier="basic", status="past_due", stripe_id="cus_123", sub_id="sub_123")
        user.subscription_period_end = datetime(2026, 6, 1)
        app_inst, get_current_user = app
        app_inst.dependency_overrides[get_current_user] = lambda: user
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("routers.billing.get_settings") as mock_settings:
            s = MagicMock()
            s.stripe_secret_key = ""
            mock_settings.return_value = s
            with TestClient(app_inst) as client:
                resp = client.get("/api/billing/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["grace_period_end"] is not None

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_no_user_id(self, app):
        from routers.billing import _handle_checkout_completed
        db = AsyncMock()
        db.get = AsyncMock(return_value=None)
        await _handle_checkout_completed({"metadata": {}}, db)
        db.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_with_referral(self, app):
        from routers.billing import _handle_checkout_completed
        user = _make_user(id=1, referred_by=2, referral_rewarded=False)
        referrer = _make_user(id=2, stripe_customer_id="cus_ref")
        db = AsyncMock()
        db.get = AsyncMock(side_effect=lambda model, pk: user if pk == 1 else referrer)
        db.commit = AsyncMock()

        with patch("routers.billing._stripe") as mock_stripe:
            mock_stripe.return_value = MagicMock()
            mock_stripe.return_value.Subscription.retrieve.return_value = {"current_period_end": 1774880000}
            mock_stripe.return_value.Customer.create_balance_transaction = MagicMock()
            await _handle_checkout_completed(
                {"metadata": {"user_id": "1", "tier": "pro"}, "subscription": "sub_123"}, db
            )
        assert user.referral_rewarded is True

    @pytest.mark.asyncio
    async def test_handle_subscription_updated_no_user(self, app):
        from routers.billing import _handle_subscription_updated
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(None))
        await _handle_subscription_updated({"customer": "cus_123"}, db)
        db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_subscription_deleted(self, app):
        from routers.billing import _handle_subscription_deleted
        user = _make_user(stripe_customer_id="cus_123")
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(user))
        db.commit = AsyncMock()

        with patch("routers.billing.send_subscription_canceled", new_callable=AsyncMock):
            await _handle_subscription_deleted({"customer": "cus_123", "current_period_end": 1774880000}, db)
        assert user.subscription_tier == "free"
        assert user.subscription_status == "canceled"

    @pytest.mark.asyncio
    async def test_handle_payment_failed(self, app):
        from routers.billing import _handle_payment_failed
        user = _make_user(stripe_customer_id="cus_123")
        db = AsyncMock()
        db.execute = AsyncMock(return_value=_make_execute_result(user))
        db.commit = AsyncMock()

        with patch("routers.billing.send_payment_failed", new_callable=AsyncMock):
            await _handle_payment_failed({"customer": "cus_123"}, db)
        assert user.subscription_status == "past_due"


# ═══════════════════════════════════════════════════════════════════════════════
# routers/broker.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestBrokerRouter:
    @pytest.fixture
    def app(self):
        from routers.broker import router
        from services.auth_svc import get_current_user
        app = FastAPI()
        app.include_router(router)
        return app, get_current_user

    def _make_app(self, app, **kw):
        app_inst, get_current_user = app
        user = _make_user(**kw)
        app_inst.dependency_overrides[get_current_user] = lambda: user
        return app_inst

    def test_broker_status_connected_alpaca(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key", alpaca_secret_enc="enc_secret")
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.decrypt_credential", side_effect=lambda x: x.replace("enc_", "")):
            with patch("services.broker_svc.verify_alpaca_connection", new_callable=AsyncMock, return_value={
                "id": "acc1", "status": "ACTIVE", "equity": "50000", "buying_power": "100000", "currency": "USD"
            }):
                with TestClient(app_inst) as client:
                    resp = client.get("/api/me/broker/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["connected"] is True
        assert data["account"]["id"] == "acc1"

    def test_broker_status_connected_ibkr(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key", auto_execute_broker="ibkr")
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.decrypt_credential", side_effect=lambda x: x.replace("enc_", "")):
            with patch("services.broker_svc.verify_ibkr_connection", new_callable=AsyncMock, return_value={
                "id": "DU123", "status": "ACTIVE", "equity": "50000", "buying_power": "100000", "currency": "USD"
            }):
                with TestClient(app_inst) as client:
                    resp = client.get("/api/me/broker/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["connected"] is True
        assert data["broker"] == "ibkr"

    def test_broker_status_decryption_failed(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key")
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.decrypt_credential", return_value=None):
            with TestClient(app_inst) as client:
                resp = client.get("/api/me/broker/status")
        assert resp.status_code == 200
        assert resp.json()["connected"] is False
        assert "decryption" in resp.json()["error"].lower()

    def test_broker_connect_alpaca_missing_secret(self, app):
        app_inst = self._make_app(app)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).post("/api/me/broker/connect", json={
            "broker": "alpaca", "account_type": "paper", "api_key": "k", "api_secret": ""
        })
        assert resp.status_code == 422

    def test_broker_connect_live_without_risk_ack(self, app):
        app_inst = self._make_app(app, risk_acknowledged=False)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).post("/api/me/broker/connect", json={
            "broker": "alpaca", "account_type": "live", "api_key": "k", "api_secret": "s"
        })
        assert resp.status_code == 403
        assert "risk acknowledgement" in resp.json()["detail"].lower()

    def test_broker_connect_success(self, app):
        app_inst = self._make_app(app, risk_acknowledged=True)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.verify_alpaca_connection", new_callable=AsyncMock, return_value={
            "id": "acc1", "status": "ACTIVE", "equity": "50000", "buying_power": "100000"
        }):
            with patch("services.broker_svc.encrypt_credential", side_effect=lambda x: f"enc_{x}"):
                with patch("services.broker_svc.current_key_version", return_value=2):
                    with patch("services.audit_svc.record_action", new_callable=AsyncMock):
                        resp = TestClient(app_inst).post("/api/me/broker/connect", json={
                            "broker": "alpaca", "account_type": "paper", "api_key": "k", "api_secret": "s"
                        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["connected"] is True

    def test_broker_disconnect(self, app):
        app_inst = self._make_app(app)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).delete("/api/me/broker/disconnect")
        assert resp.status_code == 200
        assert resp.json()["connected"] is False

    def test_broker_settings_no_credentials(self, app):
        app_inst = self._make_app(app, alpaca_key_enc=None)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).patch("/api/me/broker/settings", json={"enabled": True})
        assert resp.status_code == 422

    def test_broker_settings_success(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key")
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).patch("/api/me/broker/settings", json={
            "enabled": True, "min_conf": 80.0, "qty_dollars": 500.0
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["min_conf"] == 80.0
        assert data["qty_dollars"] == 500.0

    def test_broker_rotate_credentials(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key", risk_acknowledged=True)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.verify_alpaca_connection", new_callable=AsyncMock, return_value={
            "id": "acc1", "status": "ACTIVE", "equity": "50000"
        }):
            with patch("services.broker_svc.encrypt_credential", side_effect=lambda x: f"enc_{x}"):
                resp = TestClient(app_inst).put("/api/me/broker/rotate-credentials", json={
                    "broker": "alpaca", "account_type": "paper", "api_key": "new_k", "api_secret": "new_s"
                })
        assert resp.status_code == 200
        assert resp.json()["rotated"] is True

    def test_broker_rotate_no_existing_connection(self, app):
        app_inst = self._make_app(app, alpaca_key_enc=None)
        get_db_override, db = _mock_db()
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).put("/api/me/broker/rotate-credentials", json={
            "broker": "alpaca", "account_type": "paper", "api_key": "k", "api_secret": "s"
        })
        assert resp.status_code == 422

    def test_broker_orders(self, app):
        app_inst = self._make_app(app)
        get_db_override, db = _mock_db()
        order = BrokerOrder(
            id=1, user_id=1, signal_id="sig1", broker="alpaca", account_type="paper",
            alpaca_order_id="ord1", symbol="AAPL", notional=100.0, side="buy", status="filled"
        )
        result = MagicMock()
        result.scalars.return_value.all.return_value = [order]
        db.execute = AsyncMock(return_value=result)
        app_inst.dependency_overrides[get_db] = get_db_override
        resp = TestClient(app_inst).get("/api/me/broker/orders")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

    def test_broker_parity(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key")
        get_db_override, db = _mock_db()
        order = BrokerOrder(
            id=1, user_id=1, signal_id="sig1", broker="alpaca", account_type="paper",
            alpaca_order_id="ord1", symbol="AAPL", notional=100.0, side="buy", status="submitted"
        )
        result = MagicMock()
        result.scalars.return_value.all.return_value = [order]
        db.execute = AsyncMock(return_value=result)
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.decrypt_credential", side_effect=lambda x: x.replace("enc_", "")):
            with patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=[{"symbol": "AAPL", "qty": "10"}]):
                with TestClient(app_inst) as client:
                    resp = client.get("/api/me/broker/parity")
        assert resp.status_code == 200
        data = resp.json()
        assert data["positions_available"] is True
        assert len(data["orders"]) == 1

    def test_broker_parity_diverged(self, app):
        app_inst = self._make_app(app, alpaca_key_enc="enc_key")
        get_db_override, db = _mock_db()
        order = BrokerOrder(
            id=1, user_id=1, signal_id="sig1", broker="alpaca", account_type="paper",
            alpaca_order_id=None, symbol="AAPL", notional=100.0, side="buy", status="submitted"
        )
        result = MagicMock()
        result.scalars.return_value.all.return_value = [order]
        db.execute = AsyncMock(return_value=result)
        app_inst.dependency_overrides[get_db] = get_db_override

        with patch("services.broker_svc.decrypt_credential", side_effect=lambda x: x.replace("enc_", "")):
            with patch("services.alpaca_rest.get_positions", new_callable=AsyncMock, return_value=[]):
                with TestClient(app_inst) as client:
                    resp = client.get("/api/me/broker/parity")
        assert resp.status_code == 200
        data = resp.json()
        assert data["orders"][0]["diverged"] == "no_broker_id"


# ═══════════════════════════════════════════════════════════════════════════════
# services/dark_pool.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestDarkPool:
    def test_handle_messages_with_equity_trade(self):
        import sys
        from services.dark_pool import handle_messages
        import services.dark_pool as dp
        dp._flow_data.clear()
        dp._print_buffer.clear()

        class FakeEquityTrade:
            exchange = 4
            size = 15000
            price = 100.0
            symbol = "AAPL"

        fake_module = MagicMock()
        fake_module.EquityTrade = FakeEquityTrade
        with patch.dict(sys.modules, {"massive.websocket.models": fake_module}):
            handle_messages([FakeEquityTrade()])
        assert dp._flow_data.get("AAPL", 0) > 0
        assert len(dp._print_buffer) == 1

    def test_handle_messages_non_off_exchange(self):
        import sys
        from services.dark_pool import handle_messages
        import services.dark_pool as dp
        dp._flow_data.clear()

        class FakeEquityTrade:
            exchange = 1
            size = 15000
            price = 100.0
            symbol = "AAPL"

        fake_module = MagicMock()
        fake_module.EquityTrade = FakeEquityTrade
        with patch.dict(sys.modules, {"massive.websocket.models": fake_module}):
            handle_messages([FakeEquityTrade()])
        assert "AAPL" not in dp._flow_data

    def test_run_darkpool_scanner_no_api_key(self):
        from services.dark_pool import _run_darkpool_scanner
        with patch.dict("os.environ", {"MASSIVE_API_KEY": ""}, clear=True):
            result = _run_darkpool_scanner()
        assert result is None

    def test_run_darkpool_scanner_plan_error(self):
        from services.dark_pool import _run_darkpool_scanner
        with patch.dict("os.environ", {"MASSIVE_API_KEY": "key"}, clear=True):
            with patch("massive.WebSocketClient") as mock_client:
                mock_client.side_effect = Exception("plan limit 1008 policy violation")
                with pytest.raises(Exception):
                    _run_darkpool_scanner()

    @pytest.mark.asyncio
    async def test_start_dark_pool_stream_no_api_key(self):
        from services.dark_pool import start_dark_pool_stream
        with patch.dict("os.environ", {"MASSIVE_API_KEY": ""}, clear=True):
            task = asyncio.create_task(start_dark_pool_stream())
            await asyncio.sleep(0.05)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_start_dark_pool_stream_cancelled(self):
        from services.dark_pool import start_dark_pool_stream
        with patch.dict("os.environ", {"MASSIVE_API_KEY": "key"}, clear=True):
            task = asyncio.create_task(start_dark_pool_stream())
            await asyncio.sleep(0.05)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_get_massive_advanced_signals_no_key(self):
        from services.dark_pool import get_massive_advanced_signals
        with patch.dict("os.environ", {"POLYGON_API_KEY": "", "MASSIVE_API_KEY": ""}, clear=True):
            result = await get_massive_advanced_signals("AAPL")
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_massive_advanced_signals_with_data(self):
        from services.dark_pool import get_massive_advanced_signals
        import services.dark_pool as dp
        dp._flow_data["AAPL"] = 5.5

        def _make_cm(json_data=None, status=200):
            resp = AsyncMock()
            resp.status = status
            resp.json = AsyncMock(return_value=json_data or {})
            cm = AsyncMock()
            cm.__aenter__ = AsyncMock(return_value=resp)
            cm.__aexit__ = AsyncMock(return_value=False)
            return cm

        async def _fake_get(url, **kw):
            if "dividends" in url:
                return _make_cm({"results": [{"ex_dividend_date": "2099-01-01"}]})
            if "splits" in url:
                return _make_cm({"results": [{"execution_date": "2099-01-01"}]})
            if "ftd" in url:
                return _make_cm({"results": [{"quantity": 1000, "threshold_securities_list": True}, {"quantity": 500}]})
            return _make_cm({})

        with patch.dict("os.environ", {"POLYGON_API_KEY": "poly_key"}, clear=True):
            with patch("services.dark_pool.shared_session") as mock_session:
                session = AsyncMock()
                session.__aenter__ = AsyncMock(return_value=session)
                session.__aexit__ = AsyncMock(return_value=False)
                session.get = _fake_get
                mock_session.return_value = session
                result = await get_massive_advanced_signals("AAPL")
        assert result["dark_pool_flow"] == 5.5
        assert result["corp_actions"]["ex_div_soon"] is True
        assert result["corp_actions"]["split_soon"] is True
        assert result["ftd"]["is_reg_sho"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# services/ibkr_rest.py
# ═══════════════════════════════════════════════════════════════════════════════


class TestIbkrRest:
    def _mock_session(self, responses):
        """Build a mock aiohttp ClientSession that returns responses in order.
        responses: list of (json_data, status) tuples
        """
        idx = [0]

        def _make_cm(json_data=None, status=200):
            resp = AsyncMock()
            resp.status = status
            resp.json = AsyncMock(return_value=json_data or {})
            resp.raise_for_status = MagicMock()
            cm = AsyncMock()
            cm.__aenter__ = AsyncMock(return_value=resp)
            cm.__aexit__ = AsyncMock(return_value=False)
            return cm

        session = MagicMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)

        def _get(*a, **k):
            json_data, status = responses[idx[0]]
            idx[0] += 1
            return _make_cm(json_data, status)

        def _post(*a, **k):
            json_data, status = responses[idx[0]]
            idx[0] += 1
            return _make_cm(json_data, status)

        def _delete(*a, **k):
            json_data, status = responses[idx[0]]
            idx[0] += 1
            return _make_cm(json_data, status)

        session.get = _get
        session.post = _post
        session.delete = _delete
        return session

    @pytest.mark.asyncio
    async def test_ssl_ctx_localhost(self):
        from services.ibkr_rest import _ssl_ctx
        with patch("services.ibkr_rest._base", return_value="https://localhost:5000/v1/api"):
            assert _ssl_ctx() is False

    @pytest.mark.asyncio
    async def test_get_account_no_accounts(self):
        from services import ibkr_rest
        session = self._mock_session([([], 200)])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            with pytest.raises(ValueError, match="No IBKR accounts found"):
                await ibkr_rest.get_account("key")

    @pytest.mark.asyncio
    async def test_search_conid_not_found(self):
        from services import ibkr_rest
        session = self._mock_session([([], 200)])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            with pytest.raises(ValueError, match="Contract not found"):
                await ibkr_rest.search_conid("UNKNOWN", "key")

    @pytest.mark.asyncio
    async def test_get_positions(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000, "buyingpower": 200000}}, 200),
            ([{"symbol": "AAPL", "position": 10}], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.get_positions("key")
        assert result[0]["symbol"] == "AAPL"

    @pytest.mark.asyncio
    async def test_get_orders(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000, "buyingpower": 200000}}, 200),
            ({"orders": [{"id": "o1"}, {"id": "o2"}]}, 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.get_orders("key")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_place_order_with_reply_id(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([{"conid": 265598}], 200),
            ([{"replyId": "r123"}], 200),
            ([{"id": "o_final"}], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.place_order("key", "secret", "AAPL", 10, "buy")
        assert result["id"] == "o_final"

    @pytest.mark.asyncio
    async def test_place_notional_order(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([{"conid": 265598}], 200),
            ([{"31": "150.0"}], 200),
            ([{"id": "o1"}], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.place_notional_order("key", "secret", "AAPL", 1500.0, "buy")
        assert result["id"] == "o1"

    @pytest.mark.asyncio
    async def test_place_notional_order_cannot_determine_price(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([{"conid": 265598}], 200),
            ([], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            with pytest.raises(ValueError, match="Could not determine price"):
                await ibkr_rest.place_notional_order("key", "secret", "AAPL", 1500.0, "buy")

    @pytest.mark.asyncio
    async def test_submit_bracket_stop_order(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([{"conid": 265598}], 200),
            ([{"31": "150.0"}], 200),
            ([{"id": "bracket1"}], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.submit_bracket_stop_order(
                "key", "secret", "AAPL", 1500.0, "buy", stop_price=140.0, take_profit_price=170.0
            )
        assert result["id"] == "bracket1"

    @pytest.mark.asyncio
    async def test_submit_bracket_stop_order_no_take_profit(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([{"conid": 265598}], 200),
            ([{"31": "150.0"}], 200),
            ([{"id": "bracket2"}], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.submit_bracket_stop_order(
                "key", "secret", "AAPL", 1500.0, "buy", stop_price=140.0
            )
        assert result["id"] == "bracket2"

    @pytest.mark.asyncio
    async def test_close_position(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([{"ticker": "AAPL", "position": "10"}], 200),
            ([{"conid": 265598}], 200),
            ([{"id": "close1"}], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.close_position("key", "secret", "AAPL")
        assert result["id"] == "close1"

    @pytest.mark.asyncio
    async def test_close_position_no_position(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ([], 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.close_position("key", "secret", "AAPL")
        assert result["status"] == "no_position"

    @pytest.mark.asyncio
    async def test_cancel_order(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 100000}}, 200),
            ({"status": "cancelled"}, 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.cancel_order("key", "secret", "o123")
        assert result["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_get_portfolio_value(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 150000}}, 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.get_portfolio_value("key")
        assert result == 150000.0

    @pytest.mark.asyncio
    async def test_get_unrealized_pl(self):
        from services import ibkr_rest
        session = self._mock_session([
            ([{"id": "DU123", "currency": "USD"}], 200),
            ({"USD": {"netliquidationvalue": 150000, "unrealizedpnl": 1200}}, 200),
        ])
        with patch("services.ibkr_rest.shared_session", return_value=session):
            result = await ibkr_rest.get_unrealized_pl("key")
        assert result == 1200.0
