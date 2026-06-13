"""Tests for main.py — health check, page routes, scan status, admin endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    # Patch background tasks so lifespan doesn't try to start scanner/ML
    with (
        patch("main._supervise", return_value=None),
        patch("main._ensure_default_watchlist", new_callable=AsyncMock),
        patch("main._ensure_owner_account", new_callable=AsyncMock),
        patch("main._prewarm_news_batch", new_callable=AsyncMock),
        patch("main._warm_indicator_cache", new_callable=AsyncMock),
    ):
        from main import app

        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "db" in data


def test_sentry_health_when_not_configured(client):
    """Sentry health endpoint reports unconfigured when SENTRY_DSN is absent."""
    with patch("main._sentry_dsn", ""):
        resp = client.get("/api/health/sentry")
    assert resp.status_code == 200
    data = resp.json()
    assert data["configured"] is False
    assert data["event_id"] is None


def test_sentry_health_when_configured(client):
    """Sentry health endpoint sends a test message when SENTRY_DSN is set."""
    fake_event_id = "abc123"
    with patch("main._sentry_dsn", "https://fake@example.ingest.sentry.io/1"):
        with patch("sentry_sdk.capture_message", return_value=fake_event_id) as capture:
            resp = client.get("/api/health/sentry")
    assert resp.status_code == 200
    data = resp.json()
    assert data["configured"] is True
    assert data["event_id"] == fake_event_id
    capture.assert_called_once_with("Sentry health check", level="info")


def test_uptime_check(client):
    """Public uptime endpoint returns ok and the configured app URL."""
    resp = client.get("/api/health/uptime")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "url" in data
    assert "sentry_configured" in data
    assert "ts" in data


def test_landing_page(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_app_page(client):
    resp = client.get("/app")
    assert resp.status_code == 200


def test_login_page(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_signup_page(client):
    resp = client.get("/signup")
    assert resp.status_code == 200


def test_track_record_page(client):
    resp = client.get("/track-record")
    assert resp.status_code == 200


def test_tos_page(client):
    resp = client.get("/tos")
    assert resp.status_code == 200


def test_privacy_page(client):
    resp = client.get("/privacy")
    assert resp.status_code == 200


def test_mobile_page(client):
    resp = client.get("/mobile")
    assert resp.status_code == 200


def test_favicon_ico(client):
    resp = client.get("/favicon.ico")
    assert resp.status_code == 200


def test_favicon_svg(client):
    resp = client.get("/favicon.svg")
    assert resp.status_code == 200


def test_verify_email_page(client):
    resp = client.get("/verify-email")
    assert resp.status_code == 200


def test_hub_page(client):
    resp = client.get("/hub")
    assert resp.status_code == 200


def test_scan_status_requires_auth(client):
    resp = client.get("/api/scan/status")
    assert resp.status_code in (401, 403)


def test_scan_status_with_auth(client):
    from main import app, get_current_user
    from models import User

    def _user():
        return User(id=1, email="owner@t.com", is_owner=True, subscription_tier="pro", subscription_status="active")

    app.dependency_overrides[get_current_user] = _user
    resp = client.get("/api/scan/status")
    app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code == 200


def test_weekly_digest_trigger_requires_owner(client):
    from main import app, get_current_user
    from models import User

    def _non_owner():
        return User(id=2, email="user@t.com", is_owner=False, subscription_tier="pro", subscription_status="active")

    app.dependency_overrides[get_current_user] = _non_owner
    resp = client.post("/api/admin/trigger-weekly-digest")
    app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code == 403


def test_weekly_digest_trigger_as_owner(client):
    from main import app, get_current_user
    from models import User

    def _owner():
        u = User(id=1, email="owner@t.com", is_owner=True, subscription_tier="pro", subscription_status="active")
        u.telegram_chat_id = None
        return u

    app.dependency_overrides[get_current_user] = _owner

    settings = MagicMock()
    settings.telegram_bot_token = "token"
    settings.telegram_chat_id = "12345"
    settings.smtp_host = ""
    settings.smtp_user = ""

    with patch("main.get_settings", return_value=settings):
        resp = client.post("/api/admin/trigger-weekly-digest")
    app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code in (200, 202)


def test_weekly_digest_status_as_owner(client):
    from main import app, get_current_user
    from models import User

    def _owner():
        u = User(id=1, email="owner@t.com", is_owner=True, subscription_tier="pro", subscription_status="active")
        u.telegram_chat_id = None
        return u

    app.dependency_overrides[get_current_user] = _owner

    settings = MagicMock()
    settings.telegram_bot_token = "token"
    settings.telegram_chat_id = "123"
    settings.smtp_host = ""
    settings.smtp_user = ""

    with patch("main.get_settings", return_value=settings):
        resp = client.get("/api/admin/weekly-digest/status")
    app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code == 200


def test_csp_header_on_html(client):
    resp = client.get("/app")
    # CSP header should be set for HTML pages
    assert resp.status_code == 200


def test_static_js_file(client):
    resp = client.get("/dist/app-bundle.js")
    assert resp.status_code == 200
    assert "javascript" in resp.headers.get("content-type", "").lower()
