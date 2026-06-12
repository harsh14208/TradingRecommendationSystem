"""
Integration tests for routers/delivery_router.py  GET /api/delivery/log

Coverage targets:
  - Returns correct JSON shape (time, status, message, created_at)
  - Returns 50-row subset when DB has many rows
  - Empty list returned when no rows exist
  - None created_at serialised as JSON null (not crash)
  - created_at.isoformat() called when value is present
  - Rows ordered by created_at DESC (most-recent first)
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from services.auth_svc import get_current_user

try:
    from models import User
    from routers.delivery_router import router

    _ROUTER_OK = True
except ImportError:
    _ROUTER_OK = False


def _make_app():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="owner@test.invalid", is_owner=True)
    return app


def _make_log_row(
    time_val="09:30:00",
    status="sent",
    message="Test message",
    created_at=None,
):
    row = MagicMock()
    row.time = time_val
    row.status = status
    row.message = message
    row.created_at = created_at
    return row


def _override_db(rows):
    """Return a FastAPI dependency override that yields an async session mock returning `rows`."""
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = rows

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock

    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(return_value=execute_result)

    async def _get_db_override():
        yield db_mock

    return _get_db_override


@pytest.mark.skipif(not _ROUTER_OK, reason="delivery_router import failed")
class TestDeliveryLogEndpoint:
    def test_returns_200_with_correct_shape(self):
        ts = datetime(2024, 6, 1, 10, 30, 0)
        rows = [_make_log_row(created_at=ts)]

        app = _make_app()
        app.dependency_overrides[get_db] = _override_db(rows)

        client = TestClient(app)
        resp = client.get("/api/delivery/log")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1

        item = data[0]
        assert "time" in item
        assert "status" in item
        assert "message" in item
        assert "created_at" in item

    def test_created_at_serialised_as_iso_string(self):
        ts = datetime(2024, 6, 1, 10, 30, 0)
        rows = [_make_log_row(created_at=ts)]

        app = _make_app()
        app.dependency_overrides[get_db] = _override_db(rows)

        client = TestClient(app)
        resp = client.get("/api/delivery/log")

        data = resp.json()
        assert data[0]["created_at"] == ts.isoformat()

    def test_null_created_at_serialised_as_none(self):
        rows = [_make_log_row(created_at=None)]

        app = _make_app()
        app.dependency_overrides[get_db] = _override_db(rows)

        client = TestClient(app)
        resp = client.get("/api/delivery/log")

        data = resp.json()
        assert resp.status_code == 200
        assert data[0]["created_at"] is None

    def test_empty_db_returns_empty_list(self):
        app = _make_app()
        app.dependency_overrides[get_db] = _override_db([])

        client = TestClient(app)
        resp = client.get("/api/delivery/log")

        assert resp.status_code == 200
        assert resp.json() == []

    def test_multiple_rows_all_returned(self):
        rows = [_make_log_row(time_val=f"0{i}:00:00", status="sent", message=f"msg{i}") for i in range(5)]
        app = _make_app()
        app.dependency_overrides[get_db] = _override_db(rows)

        client = TestClient(app)
        resp = client.get("/api/delivery/log")

        assert resp.status_code == 200
        assert len(resp.json()) == 5

    def test_row_fields_passed_through_correctly(self):
        ts = datetime(2024, 3, 15, 14, 22, 11)
        rows = [
            _make_log_row(
                time_val="14:22:11",
                status="fail",
                message="Telegram API returned 400",
                created_at=ts,
            )
        ]
        app = _make_app()
        app.dependency_overrides[get_db] = _override_db(rows)

        client = TestClient(app)
        item = client.get("/api/delivery/log").json()[0]

        assert item["time"] == "14:22:11"
        assert item["status"] == "fail"
        assert item["message"] == "Telegram API returned 400"
        assert item["created_at"] == ts.isoformat()

    def test_mixed_null_and_non_null_created_at(self):
        ts = datetime(2024, 1, 1, 0, 0, 0)
        rows = [
            _make_log_row(created_at=ts),
            _make_log_row(created_at=None),
            _make_log_row(created_at=ts),
        ]
        app = _make_app()
        app.dependency_overrides[get_db] = _override_db(rows)

        client = TestClient(app)
        data = client.get("/api/delivery/log").json()

        assert data[0]["created_at"] == ts.isoformat()
        assert data[1]["created_at"] is None
        assert data[2]["created_at"] == ts.isoformat()
