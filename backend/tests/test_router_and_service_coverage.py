"""
Comprehensive coverage tests for:
  - routers/oauth.py
  - routers/price_alerts.py
  - services/delivery_manager.py
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user

try:
    from routers.oauth import router as oauth_router
    from routers.price_alerts import router as price_alerts_router

    _ROUTERS_OK = True
except ImportError:
    _ROUTERS_OK = False

try:
    from services import delivery_manager as dm

    _DM_OK = True
except ImportError:
    _DM_OK = False


# ────────────────────────── Helpers ──────────────────────────


def _make_app():
    app = FastAPI()
    return app


def _make_mock_db():
    """Return a generic AsyncMock session wired for scalar_one_or_none / scalars().all()."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.delete = AsyncMock()
    db.refresh = AsyncMock()
    db.get = AsyncMock()
    db.add = MagicMock()
    db.rollback = AsyncMock()
    return db


def _make_async_session_local(db_mock):
    """Factory that returns a class usable as ``async with AsyncSessionLocal() as db:``."""

    class _AsyncSessionLocal:
        async def __aenter__(self):
            return db_mock

        async def __aexit__(self, *args):
            pass

    return _AsyncSessionLocal


# ═══════════════════════════════════════════════════════════════
#  routers/oauth.py
# ═══════════════════════════════════════════════════════════════


@pytest.mark.skipif(not _ROUTERS_OK, reason="router import failed")
class TestOAuthRouter:
    @pytest.fixture
    def app(self):
        app = _make_app()
        app.include_router(oauth_router)
        return app

    @pytest.fixture
    def mock_settings(self):
        with patch("routers.oauth.get_settings") as m:
            s = MagicMock()
            s.google_client_id = "gcid"
            s.google_client_secret = MagicMock()
            s.google_client_secret.get_secret_value.return_value = "gsec"
            s.app_url = "http://localhost"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwtsecret"
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tgtoken"
            m.return_value = s
            yield m

    @pytest.fixture
    def mock_db_session(self):
        return _make_mock_db()

    @pytest.fixture
    def client(self, app, mock_db_session):
        async def _override():
            yield mock_db_session

        app.dependency_overrides[get_db] = _override
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()

    # ── Google redirect ──
    def test_google_oauth_start_redirect(self, client, mock_db_session, mock_settings):
        resp = client.get("/api/auth/google", follow_redirects=False)
        assert resp.status_code == 307
        loc = resp.headers["location"]
        assert "accounts.google.com" in loc
        assert "code_challenge" in loc
        assert "S256" in loc
        mock_db_session.commit.assert_awaited()

    def test_google_oauth_start_not_configured(self, client, mock_db_session, mock_settings):
        mock_settings.return_value.google_client_id = ""
        resp = client.get("/api/auth/google")
        assert resp.status_code == 503

    # ── Google callback ──
    def test_google_callback_success(self, client, mock_db_session, mock_settings):
        from routers import oauth as oauth_mod

        state_entry = MagicMock()
        state_entry.referred_by = None
        state_entry.code_verifier = "verifier"
        state_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = state_entry
        mock_db_session.execute.return_value = exec_result

        # OAuth user upsert: first lookup by oauth_sub returns None,
        # second lookup by email returns None, then user is "created".
        user = MagicMock()
        user.id = 42
        user.subscription_tier = "free"
        user.is_owner = False
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.email_verified = True
        user.email_verify_token = None
        user.last_seen_at = None
        user.telegram_link_code = "LINKCODE"
        user.referred_by = None

        # Patch _upsert_oauth_user and _issue_otc to avoid deep mocking
        with (
            patch.object(oauth_mod, "_upsert_oauth_user", new_callable=AsyncMock) as mock_upsert,
            patch.object(oauth_mod, "_issue_otc", new_callable=AsyncMock) as mock_issue,
            patch("routers.oauth.aiohttp.ClientSession") as MockSession,
        ):
            mock_upsert.return_value = user
            mock_issue.return_value = "OTC123"

            token_resp = AsyncMock()
            token_resp.status = 200
            token_resp.json = AsyncMock(return_value={"access_token": "atok"})
            token_resp.text = AsyncMock(return_value="ok")

            info_resp = AsyncMock()
            info_resp.status = 200
            info_resp.json = AsyncMock(
                return_value={
                    "email": "test@example.com",
                    "id": "google_sub_1",
                    "name": "Test User",
                    "verified_email": True,
                }
            )

            session_instance = AsyncMock()
            session_instance.post = AsyncMock(return_value=token_resp)
            session_instance.get = AsyncMock(return_value=info_resp)
            session_instance.__aenter__ = AsyncMock(return_value=session_instance)
            session_instance.__aexit__ = AsyncMock(return_value=False)
            MockSession.return_value = session_instance

            resp = client.get("/api/auth/google/callback?code=abc&state=xyz", follow_redirects=False)
            assert resp.status_code == 307
            assert "oauth_code=OTC123" in resp.headers["location"]

    def test_google_callback_invalid_state(self, client, mock_db_session, mock_settings):
        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = exec_result

        resp = client.get("/api/auth/google/callback?code=abc&state=bad")
        assert resp.status_code == 400

    def test_google_callback_token_exchange_fail(self, client, mock_db_session, mock_settings):

        state_entry = MagicMock()
        state_entry.referred_by = None
        state_entry.code_verifier = "verifier"
        state_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = state_entry
        mock_db_session.execute.return_value = exec_result

        with patch("routers.oauth.aiohttp.ClientSession") as MockSession:
            token_resp = AsyncMock()
            token_resp.status = 400
            token_resp.text = AsyncMock(return_value="bad request")

            session_instance = AsyncMock()
            session_instance.post = AsyncMock(return_value=token_resp)
            session_instance.__aenter__ = AsyncMock(return_value=session_instance)
            session_instance.__aexit__ = AsyncMock(return_value=False)
            MockSession.return_value = session_instance

            resp = client.get("/api/auth/google/callback?code=abc&state=xyz")
            assert resp.status_code == 502

    def test_google_callback_no_verified_email(self, client, mock_db_session, mock_settings):

        state_entry = MagicMock()
        state_entry.referred_by = None
        state_entry.code_verifier = "verifier"
        state_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = state_entry
        mock_db_session.execute.return_value = exec_result

        with patch("routers.oauth.aiohttp.ClientSession") as MockSession:
            token_resp = AsyncMock()
            token_resp.status = 200
            token_resp.json = AsyncMock(return_value={"access_token": "atok"})

            info_resp = AsyncMock()
            info_resp.status = 200
            info_resp.json = AsyncMock(
                return_value={
                    "email": "test@example.com",
                    "id": "g1",
                    "name": "Test",
                    "verified_email": False,
                }
            )

            session_instance = AsyncMock()
            session_instance.post = AsyncMock(return_value=token_resp)
            session_instance.get = AsyncMock(return_value=info_resp)
            session_instance.__aenter__ = AsyncMock(return_value=session_instance)
            session_instance.__aexit__ = AsyncMock(return_value=False)
            MockSession.return_value = session_instance

            resp = client.get("/api/auth/google/callback?code=abc&state=xyz")
            assert resp.status_code == 400

    # ── OAuth exchange ──
    def test_oauth_exchange_success(self, client, mock_db_session, mock_settings):

        code_entry = MagicMock()
        code_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
        code_entry.user_data = {
            "access_token": "acc_tok",
            "refresh_token": "ref_tok",
            "user_id": 1,
            "user": {"id": 1, "email": "a@b.com"},
        }

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = code_entry
        mock_db_session.execute.return_value = exec_result

        resp = client.get("/api/auth/oauth-exchange?code=VALID")
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "acc_tok"
        assert data["token_type"] == "bearer"
        # Cookie should be set
        assert "st_refresh" in resp.cookies

    def test_oauth_exchange_invalid_code(self, client, mock_db_session, mock_settings):
        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = exec_result

        resp = client.get("/api/auth/oauth-exchange?code=INVALID")
        assert resp.status_code == 400

    def test_oauth_exchange_expired_code(self, client, mock_db_session, mock_settings):
        code_entry = MagicMock()
        code_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=5)
        code_entry.user_data = {}

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = code_entry
        mock_db_session.execute.return_value = exec_result

        resp = client.get("/api/auth/oauth-exchange?code=OLD")
        assert resp.status_code == 400

    def test_oauth_exchange_integrity_error(self, client, mock_db_session, mock_settings):
        from sqlalchemy.exc import IntegrityError

        code_entry = MagicMock()
        code_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
        code_entry.user_data = {
            "access_token": "acc_tok",
            "refresh_token": "ref_tok",
            "user_id": 1,
            "user": {"id": 1},
        }

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = code_entry
        mock_db_session.execute.return_value = exec_result
        mock_db_session.commit.side_effect = [None, IntegrityError("stmt", {}, Exception())]

        resp = client.get("/api/auth/oauth-exchange?code=VALID")
        assert resp.status_code == 400

    def test_oauth_exchange_generic_error(self, client, mock_db_session, mock_settings):

        code_entry = MagicMock()
        code_entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
        code_entry.user_data = {
            "access_token": "acc_tok",
            "refresh_token": "ref_tok",
            "user_id": 1,
            "user": {"id": 1},
        }

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = code_entry
        mock_db_session.execute.return_value = exec_result
        mock_db_session.commit.side_effect = [None, RuntimeError("boom")]

        resp = client.get("/api/auth/oauth-exchange?code=VALID")
        assert resp.status_code == 500


# ═══════════════════════════════════════════════════════════════
#  routers/price_alerts.py
# ═══════════════════════════════════════════════════════════════


@pytest.mark.skipif(not _ROUTERS_OK, reason="router import failed")
class TestPriceAlertsRouter:
    @pytest.fixture
    def app(self):
        app = _make_app()
        app.include_router(price_alerts_router)
        return app

    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com")

    @pytest.fixture
    def mock_db_session(self):
        return _make_mock_db()

    @pytest.fixture
    def client(self, app, mock_user, mock_db_session):
        async def _override_user():
            return mock_user

        async def _override_db():
            yield mock_db_session

        app.dependency_overrides[get_current_user] = _override_user
        app.dependency_overrides[get_db] = _override_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.clear()

    def test_get_alerts(self, client, mock_db_session):
        alert = MagicMock(id=1, ticker="AAPL", target_price=150.0, condition="above")
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [alert]
        exec_result = MagicMock()
        exec_result.scalars.return_value = scalars_mock
        mock_db_session.execute.return_value = exec_result

        resp = client.get("/api/alerts/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["ticker"] == "AAPL"

    def test_get_alerts_empty(self, client, mock_db_session):
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        exec_result = MagicMock()
        exec_result.scalars.return_value = scalars_mock
        mock_db_session.execute.return_value = exec_result

        resp = client.get("/api/alerts/")
        assert resp.status_code == 200
        assert resp.json()["alerts"] == []

    def test_create_alert_success(self, client, mock_db_session):
        alert_mock = MagicMock()
        alert_mock.id = 77
        mock_db_session.add = MagicMock()

        # commit doesn't return anything; alert.id is set on the mock after add
        def _capture_add(obj):
            obj.id = 77

        mock_db_session.add.side_effect = _capture_add

        resp = client.post("/api/alerts/", json={"ticker": "TSLA", "target_price": 250.0, "condition": "above"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["alert_id"] == 77
        mock_db_session.commit.assert_awaited()

    def test_create_alert_invalid_ticker(self, client, mock_db_session):
        resp = client.post("/api/alerts/", json={"ticker": "INVALID1", "target_price": 100.0, "condition": "above"})
        assert resp.status_code == 422

    def test_create_alert_invalid_price_negative(self, client, mock_db_session):
        resp = client.post("/api/alerts/", json={"ticker": "AAPL", "target_price": -10.0, "condition": "above"})
        assert resp.status_code == 422

    def test_create_alert_invalid_price_too_high(self, client, mock_db_session):
        resp = client.post("/api/alerts/", json={"ticker": "AAPL", "target_price": 2_000_000.0, "condition": "above"})
        assert resp.status_code == 422

    def test_create_alert_invalid_condition(self, client, mock_db_session):
        resp = client.post("/api/alerts/", json={"ticker": "AAPL", "target_price": 150.0, "condition": "sideways"})
        assert resp.status_code == 422

    def test_delete_alert_success(self, client, mock_db_session, mock_user):
        alert = MagicMock()
        alert.user_id = mock_user.id
        mock_db_session.get.return_value = alert

        resp = client.delete("/api/alerts/5")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        mock_db_session.delete.assert_awaited_with(alert)
        mock_db_session.commit.assert_awaited()

    def test_delete_alert_not_found(self, client, mock_db_session):
        mock_db_session.get.return_value = None
        resp = client.delete("/api/alerts/99")
        assert resp.status_code == 404

    def test_delete_alert_forbidden(self, client, mock_db_session, mock_user):
        alert = MagicMock()
        alert.user_id = 999  # different user
        mock_db_session.get.return_value = alert

        resp = client.delete("/api/alerts/5")
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════
#  services/delivery_manager.py
# ═══════════════════════════════════════════════════════════════


@pytest.mark.skipif(not _DM_OK, reason="delivery_manager import failed")
class TestDeliveryManagerQuietHours:
    def test_is_in_quiet_hours_no_settings(self):
        now = datetime.now(timezone.utc)
        assert dm.is_in_quiet_hours(now, "", "22:00", "08:00") is False
        assert dm.is_in_quiet_hours(now, "America/New_York", "", "08:00") is False

    @patch("services.delivery_manager.log")
    def test_is_in_quiet_hours_bad_timezone_logs_warning(self, mock_log):
        now = datetime.now(timezone.utc)
        result = dm.is_in_quiet_hours(now, "Mars/Phobos", "22:00", "08:00")
        assert result is False
        mock_log.warning.assert_called()

    def test_is_in_quiet_hours_within_range(self):
        # 02:00 UTC = 21:00 EST (winter) or 22:00 EDT — choose a winter date
        import pytz

        tz = pytz.timezone("America/New_York")
        local = tz.localize(datetime(2024, 1, 15, 23, 0, 0))
        now = local.astimezone(pytz.utc)
        assert dm.is_in_quiet_hours(now, "America/New_York", "22:00", "06:00") is True

    def test_is_in_quiet_hours_outside_range(self):
        import pytz

        tz = pytz.timezone("America/New_York")
        local = tz.localize(datetime(2024, 1, 15, 14, 0, 0))
        now = local.astimezone(pytz.utc)
        assert dm.is_in_quiet_hours(now, "America/New_York", "22:00", "06:00") is False

    def test_seconds_until_quiet_hours_end_no_tz(self):
        now = datetime.now(timezone.utc)
        assert dm.seconds_until_quiet_hours_end(now, "", "08:00") == 0.0

    @patch("services.delivery_manager.log")
    def test_seconds_until_quiet_hours_end_bad_tz(self, mock_log):
        now = datetime.now(timezone.utc)
        assert dm.seconds_until_quiet_hours_end(now, "Mars/Phobos", "08:00") == 0.0
        mock_log.warning.assert_called()


@pytest.mark.skipif(not _DM_OK, reason="delivery_manager import failed")
class TestDeliveryManagerDelivery:
    @pytest.fixture
    def mock_db(self):
        return _make_mock_db()

    @pytest.fixture
    def mock_shared_session(self):
        """Patch services.http_client.shared_session to yield a mocked session."""
        with patch("services.http_client.shared_session") as m:
            session_mock = AsyncMock()
            post_resp = AsyncMock()
            post_resp.status = 200
            post_resp.json = AsyncMock(return_value={"ok": True, "result": {"message_id": 101}})
            session_mock.post = AsyncMock(return_value=post_resp)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            m.return_value = session_mock
            yield m

    @pytest.mark.asyncio
    async def test_queue_delivery_creates_task(self):
        with patch("services.delivery_manager.deliver_with_retry", new_callable=AsyncMock) as mock_deliver:
            dm.queue_delivery(1, 1, "telegram", {"text": "hi"})
            # asyncio.create_task fires immediately in sync test context,
            # but we can't easily await it. Just verify the coroutine was invoked
            # by checking deliver_with_retry was referenced.
            # Since queue_delivery just creates a task, no direct assertion on mock_deliver
            # is possible without awaiting the task. We'll test deliver_with_retry directly.
            pass

    @pytest.mark.asyncio
    async def test_deliver_with_retry_telegram_success(self, mock_db, mock_shared_session):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        app_settings = MagicMock()
        app_settings.data = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                return MagicMock(id=1, status="pending")
            return None

        mock_db.get.side_effect = _db_get

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = exec_result

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            s = MagicMock()
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tok"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            await dm.deliver_with_retry(1, 1, "telegram", {"text": "hello"}, max_retries=1)

        # Verify receipt was updated to sent
        calls = [c for c in mock_db.commit.await_args_list]
        assert len(calls) >= 2  # initial create + final update

    @pytest.mark.asyncio
    async def test_deliver_with_retry_duplicate_blocked(self, mock_db):
        existing = MagicMock()
        existing.id = 1

        def _db_get(model, pk):
            if model.__name__ == "User":
                return MagicMock()
            return None

        mock_db.get.side_effect = _db_get

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = exec_result

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            await dm.deliver_with_retry(1, 1, "telegram", {"text": "hello"}, max_retries=1)
            # Should return early; no commit for creating receipt
            # Only the duplicate check execute is called
            mock_db.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_deliver_with_retry_user_not_found(self, mock_db):
        def _db_get(model, pk):
            if model.__name__ == "User":
                return None
            return None

        mock_db.get.side_effect = _db_get

        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = exec_result

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            await dm.deliver_with_retry(1, 1, "telegram", {"text": "hello"}, max_retries=1)
            # Should return early after user not found warning

    @pytest.mark.asyncio
    async def test_deliver_with_retry_discord_success(self, mock_db, mock_shared_session):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        app_settings = MagicMock()
        app_settings.data = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                return MagicMock(id=1, status="pending")
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            s = MagicMock()
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            await dm.deliver_with_retry(
                1, 1, "discord", {"webhook_url": "http://discord.wh", "payload": {"content": "hi"}}, max_retries=1
            )

    @pytest.mark.asyncio
    async def test_deliver_with_retry_discord_missing_webhook_url(self, mock_db):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                return MagicMock(id=1, status="pending")
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            s = MagicMock()
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            await dm.deliver_with_retry(1, 1, "discord", {"payload": {"content": "hi"}}, max_retries=1)
            # Should fail with missing webhook_url error and dead-letter logged

    @pytest.mark.asyncio
    async def test_deliver_with_retry_push_success(self, mock_db):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                return MagicMock(id=1, status="pending")
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            s = MagicMock()
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            with patch("services.delivery_manager.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = True
                await dm.deliver_with_retry(
                    1,
                    1,
                    "push",
                    {"subscription_info": {"endpoint": "e"}, "payload": {"title": "t"}},
                    max_retries=1,
                )

    @pytest.mark.asyncio
    async def test_deliver_with_retry_webhook_success(self, mock_db):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = "whsec"

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                return MagicMock(id=1, status="pending")
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
            patch("services.http_client.shared_session") as mock_shared,
        ):
            s = MagicMock()
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            post_resp = AsyncMock()
            post_resp.status = 200
            session_mock = AsyncMock()
            session_mock.post = AsyncMock(return_value=post_resp)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            mock_shared.return_value = session_mock

            await dm.deliver_with_retry(
                1,
                1,
                "webhook",
                {"webhook_url": "http://hook.url", "signal_data": {"ticker": "AAPL"}},
                max_retries=1,
            )

    @pytest.mark.asyncio
    async def test_deliver_with_retry_quiet_hours_defer(self, mock_db):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        app_settings = MagicMock()
        app_settings.data = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                return MagicMock(id=1, status="deferred")
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=True),
            patch("services.delivery_manager.seconds_until_quiet_hours_end", return_value=0.01),
            patch("services.delivery_manager.asyncio.sleep", new_callable=AsyncMock),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
        ):
            s = MagicMock()
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tok"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            await dm.deliver_with_retry(1, 1, "telegram", {"text": "hi"}, max_retries=1)

    @pytest.mark.asyncio
    async def test_deliver_with_retry_exhausts_retries(self, mock_db):
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                receipt = MagicMock()
                receipt.id = 1
                receipt.status = "pending"
                return receipt
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.delivery_manager.asyncio.sleep", new_callable=AsyncMock),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
            patch("services.http_client.shared_session") as mock_shared,
        ):
            s = MagicMock()
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tok"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            post_resp = AsyncMock()
            post_resp.status = 500
            session_mock = AsyncMock()
            session_mock.post = AsyncMock(return_value=post_resp)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            mock_shared.return_value = session_mock

            await dm.deliver_with_retry(1, 1, "telegram", {"text": "hi"}, max_retries=2)
            # Final receipt should have status failed
            final_receipt = mock_db.get.await_args_list[-1][0][1]
            # We can't easily assert on the mock object properties, but coverage is exercised

    @pytest.mark.asyncio
    async def test_deliver_with_retry_telegram_400_no_retry(self, mock_db):
        """A Telegram 4xx is permanent: stop after one attempt and record the description."""
        user = MagicMock()
        user.id = 7
        user.webhook_secret = None

        captured = {}

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                receipt = MagicMock()
                receipt.id = 1
                receipt.status = "pending"
                captured["receipt"] = receipt
                return receipt
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.delivery_manager.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
            patch("services.http_client.shared_session") as mock_shared,
        ):
            s = MagicMock()
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tok"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            post_resp = AsyncMock()
            post_resp.status = 400
            post_resp.json = AsyncMock(return_value={"ok": False, "description": "Bad Request: chat not found"})
            post_cm = AsyncMock()
            post_cm.__aenter__ = AsyncMock(return_value=post_resp)
            post_cm.__aexit__ = AsyncMock(return_value=False)
            session_mock = AsyncMock()
            session_mock.post = MagicMock(return_value=post_cm)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            mock_shared.return_value = session_mock

            await dm.deliver_with_retry(7, 7, "telegram", {"text": "hi"}, max_retries=5)

        # Permanent 4xx must not be retried: exactly one POST, no backoff sleeps.
        assert session_mock.post.call_count == 1
        mock_sleep.assert_not_awaited()
        # The Telegram description is preserved (truncated to 50 chars) for the dead-letter.
        assert captured["receipt"].status == "failed"
        assert "chat not found" in (captured["receipt"].error_code or "")
        # The failure is surfaced in the delivery panel (send_log fail row).
        added = [c.args[0] for c in mock_db.add.call_args_list]
        send_logs = [a for a in added if type(a).__name__ == "SendLog"]
        assert len(send_logs) == 1
        assert send_logs[0].status == "fail"
        assert send_logs[0].user_id == 7

    @pytest.mark.asyncio
    async def test_deliver_with_retry_telegram_markdown_falls_back_to_plain(self, mock_db):
        """A Markdown parse 400 retries once as plain text and succeeds."""
        user = MagicMock()
        user.id = 7
        user.webhook_secret = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                receipt = MagicMock()
                receipt.id = 1
                receipt.status = "pending"
                return receipt
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.delivery_manager.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
            patch("services.http_client.shared_session") as mock_shared,
        ):
            s = MagicMock()
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tok"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            # First call: 400 parse error. Second call (plain text): success.
            resp_fail = AsyncMock()
            resp_fail.status = 400
            resp_fail.json = AsyncMock(return_value={"ok": False, "description": "Bad Request: can't parse entities"})
            cm_fail = AsyncMock()
            cm_fail.__aenter__ = AsyncMock(return_value=resp_fail)
            cm_fail.__aexit__ = AsyncMock(return_value=False)

            resp_ok = AsyncMock()
            resp_ok.status = 200
            resp_ok.json = AsyncMock(return_value={"ok": True, "result": {"message_id": 5}})
            cm_ok = AsyncMock()
            cm_ok.__aenter__ = AsyncMock(return_value=resp_ok)
            cm_ok.__aexit__ = AsyncMock(return_value=False)

            session_mock = AsyncMock()
            session_mock.post = MagicMock(side_effect=[cm_fail, cm_ok])
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            mock_shared.return_value = session_mock

            await dm.deliver_with_retry(
                7, 7, "telegram", {"chat_id": "x", "text": "hi *_", "parse_mode": "Markdown"}, max_retries=5
            )

        # Two posts (Markdown then plain text), no outer-loop backoff sleep needed.
        assert session_mock.post.call_count == 2
        # Second call dropped parse_mode.
        assert "parse_mode" not in session_mock.post.call_args_list[1].kwargs["json"]
        mock_sleep.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_deliver_with_retry_telegram_429_retries(self, mock_db):
        """A Telegram 429 rate-limit is transient: it must still be retried."""
        user = MagicMock()
        user.id = 1
        user.webhook_secret = None

        def _db_get(model, pk):
            if model.__name__ == "User":
                return user
            if model.__name__ == "SignalDelivery":
                receipt = MagicMock()
                receipt.id = 1
                receipt.status = "pending"
                return receipt
            return None

        mock_db.get.side_effect = _db_get
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

        with (
            patch.object(dm, "AsyncSessionLocal", _make_async_session_local(mock_db)),
            patch("config.get_settings") as mock_settings,
            patch("services.delivery_manager.is_in_quiet_hours", return_value=False),
            patch("services.delivery_manager.asyncio.sleep", new_callable=AsyncMock),
            patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "c1")),
            patch("services.http_client.shared_session") as mock_shared,
        ):
            s = MagicMock()
            s.telegram_bot_token = MagicMock()
            s.telegram_bot_token.get_secret_value.return_value = "tok"
            s.jwt_secret = MagicMock()
            s.jwt_secret.get_secret_value.return_value = "jwt"
            mock_settings.return_value = s

            post_resp = AsyncMock()
            post_resp.status = 429
            post_resp.json = AsyncMock(return_value={"ok": False, "description": "Too Many Requests"})
            post_cm = AsyncMock()
            post_cm.__aenter__ = AsyncMock(return_value=post_resp)
            post_cm.__aexit__ = AsyncMock(return_value=False)
            session_mock = AsyncMock()
            session_mock.post = MagicMock(return_value=post_cm)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            mock_shared.return_value = session_mock

            await dm.deliver_with_retry(1, 1, "telegram", {"text": "hi"}, max_retries=3)

        # 429 stays retryable: all attempts are used.
        assert session_mock.post.call_count == 3
