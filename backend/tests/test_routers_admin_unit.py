"""Tests for routers/admin.py — owner-only admin endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


def _make_app(is_owner=True):
    from routers.admin import router

    app = FastAPI()
    app.include_router(router)

    def _user():
        return User(id=1, email="owner@t.com", is_owner=is_owner, subscription_tier="pro", subscription_status="active")

    app.dependency_overrides[get_current_user] = _user
    return app


def _mock_db(signals=None, users=None, snapshots=None, deliveries=None):
    mock_db = MagicMock()
    sig_result = MagicMock()
    sig_result.scalars.return_value.all.return_value = signals or []
    sig_result.scalar_one_or_none.return_value = None

    user_result = MagicMock()
    user_result.scalars.return_value.all.return_value = users or []

    snap_result = MagicMock()
    snap_result.scalars.return_value.all.return_value = snapshots or []

    call_count = [0]

    async def _execute(query):
        call_count[0] += 1
        if call_count[0] % 4 == 1:
            return sig_result
        elif call_count[0] % 4 == 2:
            return user_result
        elif call_count[0] % 4 == 3:
            return snap_result
        return sig_result

    mock_db.execute = AsyncMock(side_effect=_execute)

    async def _get_db():
        yield mock_db

    return _get_db


def test_setup_status_owner():
    app = _make_app(is_owner=True)
    app.dependency_overrides[get_db] = _mock_db()
    settings = MagicMock()
    settings.jwt_secret = "a_very_long_jwt_secret_here"
    settings.owner_email = "owner@t.com"
    settings.owner_password = "SecurePassword1234!"
    settings.telegram_bot_token = "token123"
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_webhook_secret = "whsec_123"
    settings.stripe_price_basic = "price_basic"
    settings.stripe_price_pro = "price_pro"
    settings.app_url = "https://signal.trade"
    settings.smtp_host = "smtp.gmail.com"
    settings.finnhub_api_key = "fh_key"
    settings.polygon_api_key = "poly_key"
    settings.google_client_id = ""
    settings.discord_client_id = ""

    with patch("routers.admin.get_settings", return_value=settings):
        with TestClient(app) as client:
            resp = client.get("/api/admin/setup-status")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "checks" in data
    assert isinstance(data["checks"], list)


def test_setup_status_non_owner():
    app = _make_app(is_owner=False)
    app.dependency_overrides[get_db] = _mock_db()
    with TestClient(app) as client:
        resp = client.get("/api/admin/setup-status")
    assert resp.status_code == 403


def test_stats_endpoint():
    users = []
    for i in range(3):
        u = MagicMock(spec=User)
        u.id = i + 1
        u.subscription_tier = "basic"
        u.subscription_status = "active"
        u.is_owner = False
        u.created_at = datetime(2026, 1, 1)
        users.append(u)

    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = users
    result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/admin/stats")
    assert resp.status_code == 200


def test_users_list():
    users = []
    for i in range(2):
        u = MagicMock(spec=User)
        u.id = i + 1
        u.email = f"user{i}@t.com"
        u.full_name = f"User {i}"
        u.subscription_tier = "free"
        u.subscription_status = "active"
        u.is_owner = False
        u.created_at = datetime(2026, 1, 1)
        u.telegram_chat_id = None
        users.append(u)

    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = users
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/admin/users")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_live_wr_stats():
    signals = []
    for i in range(5):
        s = MagicMock()
        s.is_sent = True
        s.action = "BUY"
        s.outcome_pct = 1.5 if i % 2 == 0 else -0.5
        s.outcome_1d = None
        s.outcome_3d = None
        s.outcome_14d = None
        s.exit_type = None
        s.created_at = datetime(2026, 3, i + 1)
        s.ticker = "AAPL"
        s.confidence = 70.0
        signals.append(s)

    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/admin/live-wr-stats")
    assert resp.status_code == 200


@patch("routers.admin.get_settings")
@patch("services.broker_svc.verify_alpaca_connection")
@patch("services.http_client.shared_session")
def test_system_readiness(mock_shared_session, mock_verify_alpaca, mock_get_settings):
    from contextlib import asynccontextmanager

    # Mock settings
    settings = MagicMock()
    settings.jwt_secret = "secret"
    settings.owner_email = "owner@t.com"
    settings.owner_password = "SecurePassword1234!"
    settings.telegram_bot_token = "token"
    settings.stripe_secret_key = "sk"
    settings.stripe_webhook_secret = "whsec_stripe"
    settings.stripe_price_basic = "price_basic"
    settings.stripe_price_pro = "price_pro"
    settings.app_url = "https://app.com"
    settings.alpaca_api_key = "key"
    settings.alpaca_api_secret = "secret"
    settings.finnhub_api_key = "key"
    settings.fred_api_key = "key"
    settings.polygon_api_key = "key"
    settings.redis_url = ""  # no redis check
    mock_get_settings.return_value = settings

    # Mock Alpaca verification
    mock_verify_alpaca.return_value = {"status": "ACTIVE"}

    # Mock aiohttp session and responses
    mock_session = MagicMock()

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"ok": True, "result": {"url": "https://app.com/api/telegram/webhook"}})

    class FakeAsyncContextManager:
        async def __aenter__(self):
            return mock_resp

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_session.get.return_value = FakeAsyncContextManager()

    @asynccontextmanager
    async def fake_shared_session():
        yield mock_session

    mock_shared_session.return_value = fake_shared_session()

    mock_db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = MagicMock(data={"execution_paused": False})
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/admin/system-readiness")

    assert resp.status_code == 200
    data = resp.json()
    assert data["ready"] is True
    assert data["kill_switch"]["execution_paused"] is False
    assert data["database"]["status"] == "ok"
    assert data["env_vars"]["status"] == "ok"
    assert data["providers"]["alpaca"]["status"] == "ok"
    assert data["providers"]["finnhub"]["status"] == "ok"
    assert data["webhooks"]["telegram"]["status"] == "ok"
    assert data["webhooks"]["stripe"]["status"] == "ok"
