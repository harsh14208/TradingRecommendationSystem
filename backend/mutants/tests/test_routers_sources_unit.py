"""Tests for routers/sources.py — data source list and toggle endpoints."""

from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import Source, User
from services.auth_svc import get_current_user


def _src(id_, is_on=True):
    s = MagicMock(spec=Source)
    s.id = id_
    s.name = f"Source {id_}"
    s.abbr = id_.upper()
    s.description = f"desc {id_}"
    s.is_on = is_on
    s.requests_24h = 0
    s.latency_ms = 100
    s.feed = "1h"
    return s


def _make_app():
    from routers.sources import router

    app = FastAPI()
    app.include_router(router)

    def _user():
        return User(id=1, email="t@t.com", is_owner=True, subscription_tier="pro")

    app.dependency_overrides[get_current_user] = _user
    return app


def _mock_db(sources, get_src=None):
    mock_db = MagicMock()

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = sources

    single_result = MagicMock()
    single_result.scalar_one_or_none.return_value = get_src

    async def _execute(query):
        # Toggle/PATCH queries select by id (single result); list queries return all
        if get_src is not None:
            return single_result
        return list_result

    mock_db.execute = AsyncMock(side_effect=_execute)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db


def test_list_sources():
    sources = [_src("yf"), _src("fh"), _src("tech")]
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(sources)
    with TestClient(app) as client:
        resp = client.get("/api/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["id"] == "yf"


def test_toggle_source_with_body():
    src = _src("yf", is_on=True)
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([], get_src=src)
    with TestClient(app) as client:
        resp = client.patch("/api/sources/yf", json={"is_on": False})
    assert resp.status_code == 200
    assert src.is_on is False


def test_toggle_source_no_body():
    src = _src("fh", is_on=True)
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([], get_src=src)
    with TestClient(app) as client:
        resp = client.patch("/api/sources/fh")
    assert resp.status_code == 200
    # Should toggle: True -> False
    assert src.is_on is False


def test_toggle_source_put():
    src = _src("tech", is_on=False)
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([], get_src=src)
    with TestClient(app) as client:
        resp = client.put("/api/sources/tech", json={"is_on": True})
    assert resp.status_code == 200
    assert src.is_on is True


def test_toggle_source_not_found():
    # Separate mock that returns None for scalar_one_or_none
    mock_db = MagicMock()
    not_found_result = MagicMock()
    not_found_result.scalar_one_or_none.return_value = None

    mock_db.execute = AsyncMock(return_value=not_found_result)
    mock_db.commit = AsyncMock()

    async def _get_db():
        yield mock_db

    app = _make_app()
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        resp = client.patch("/api/sources/nonexistent")
    assert resp.status_code == 404
