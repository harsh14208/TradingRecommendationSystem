"""Tests for routers/push.py — web push subscription endpoint."""

from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import PushSubscription, User
from services.auth_svc import get_current_user


def _make_app():
    from routers.push import router

    app = FastAPI()
    app.include_router(router)

    def _user():
        return User(id=1, email="t@t.com", is_owner=False, subscription_tier="basic")

    app.dependency_overrides[get_current_user] = _user
    return app


def _mock_db(existing_sub=None):
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_sub
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db


def test_subscribe_new():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(existing_sub=None)
    payload = {
        "endpoint": "https://push.example.com/endpoint123",
        "keys": {"p256dh": "key123", "auth": "auth123"},
    }
    with TestClient(app) as client:
        resp = client.post("/api/push/subscribe", json=payload)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_subscribe_already_exists():
    existing = MagicMock(spec=PushSubscription)
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(existing_sub=existing)
    payload = {
        "endpoint": "https://push.example.com/endpoint123",
        "keys": {"p256dh": "key123", "auth": "auth123"},
    }
    with TestClient(app) as client:
        resp = client.post("/api/push/subscribe", json=payload)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_subscribe_missing_endpoint():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    payload = {"keys": {"p256dh": "key123", "auth": "auth123"}}
    with TestClient(app) as client:
        resp = client.post("/api/push/subscribe", json=payload)
    assert resp.status_code == 400


def test_subscribe_missing_p256dh():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    payload = {
        "endpoint": "https://push.example.com/ep",
        "keys": {"auth": "auth123"},
    }
    with TestClient(app) as client:
        resp = client.post("/api/push/subscribe", json=payload)
    assert resp.status_code == 400


def test_subscribe_missing_auth():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db()
    payload = {
        "endpoint": "https://push.example.com/ep",
        "keys": {"p256dh": "key123"},
    }
    with TestClient(app) as client:
        resp = client.post("/api/push/subscribe", json=payload)
    assert resp.status_code == 400
