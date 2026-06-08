import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import User
from routers.settings_router import router
from services.auth_svc import get_current_user
from services.delivery_manager import (
    is_in_quiet_hours,
    seconds_until_quiet_hours_end,
)


# Test helper functions
def test_is_in_quiet_hours():
    # 1. Normal quiet hours (e.g. 22:00 to 08:00 next day)
    # 23:00 UTC is 19:00 EST. Not in quiet hours.
    now_utc = datetime(2026, 6, 8, 23, 0, tzinfo=timezone.utc)
    assert not is_in_quiet_hours(now_utc, "America/New_York", "22:00", "08:00")

    # 03:00 UTC next day is 23:00 EST. In quiet hours.
    now_utc_night = datetime(2026, 6, 9, 3, 0, tzinfo=timezone.utc)
    assert is_in_quiet_hours(now_utc_night, "America/New_York", "22:00", "08:00")

    # 2. Quiet hours not crossing midnight (e.g. 13:00 to 17:00)
    # 18:00 UTC is 14:00 EST. In quiet hours.
    now_utc_day = datetime(2026, 6, 8, 18, 0, tzinfo=timezone.utc)
    assert is_in_quiet_hours(now_utc_day, "America/New_York", "13:00", "17:00")

    # 12:00 UTC is 08:00 EST. Not in quiet hours.
    assert not is_in_quiet_hours(now_utc_day.replace(hour=12), "America/New_York", "13:00", "17:00")


def test_seconds_until_quiet_hours_end():
    # 03:00 UTC is 23:00 EST. Quiet hours end at 08:00 EST.
    # Time remaining is 9 hours = 32400 seconds.
    now_utc = datetime(2026, 6, 9, 3, 0, tzinfo=timezone.utc)
    secs = seconds_until_quiet_hours_end(now_utc, "America/New_York", "08:00")
    assert abs(secs - 32400) < 10

    # 18:00 UTC is 14:00 EST. Quiet hours end at 17:00 EST.
    # Time remaining is 3 hours = 10800 seconds.
    now_utc_day = datetime(2026, 6, 8, 18, 0, tzinfo=timezone.utc)
    secs_day = seconds_until_quiet_hours_end(now_utc_day, "America/New_York", "17:00")
    assert abs(secs_day - 10800) < 10


# Router API test setup
app = FastAPI()
app.include_router(router, prefix="")


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def client(mock_db):
    user = User(
        id=101, email="webhook@example.com", webhook_url="https://example.com/receive", webhook_secret="old_secret_123"
    )

    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_get_webhook_secret(client, mock_db):
    user = User(
        id=101, email="webhook@example.com", webhook_url="https://example.com/receive", webhook_secret="old_secret_123"
    )
    mock_db.get.return_value = user

    response = client.get("/api/settings/webhooks/secret")
    assert response.status_code == 200
    assert response.json()["webhook_secret"] == "old_secret_123"


def test_rotate_webhook_secret(client, mock_db):
    user = User(
        id=101, email="webhook@example.com", webhook_url="https://example.com/receive", webhook_secret="old_secret_123"
    )
    mock_db.get.return_value = user

    response = client.post("/api/settings/webhooks/rotate-secret")
    assert response.status_code == 200
    new_secret = response.json()["webhook_secret"]
    assert new_secret != "old_secret_123"
    assert len(new_secret) == 64  # token_hex(32)
    assert user.webhook_secret == new_secret
    mock_db.commit.assert_called_once()


@patch("aiohttp.ClientSession.post")
def test_test_webhook_success(mock_post, client, mock_db):
    user = User(
        id=101, email="webhook@example.com", webhook_url="https://example.com/receive", webhook_secret="old_secret_123"
    )
    mock_db.get.return_value = user

    # Mock success HTTP response
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.text.return_value = "Verified"

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_resp
    mock_post.return_value = mock_context

    response = client.post("/api/settings/webhooks/test")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == 200
    assert data["response"] == "Verified"
