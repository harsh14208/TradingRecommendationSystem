"""Tests for admin.py pure helper functions and endpoints."""

from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


def _make_owner():
    u = User(id=1, email="o@t.com", is_owner=True, subscription_tier="pro", subscription_status="active")
    u.full_name = "Owner"
    return u


def _make_app():
    from routers.admin import router

    app = FastAPI()
    app.include_router(router)
    return app


def _mock_db(signals=None):
    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals or []
    result.scalar_one_or_none.return_value = None
    result.scalar.return_value = 0
    mock_db.execute = AsyncMock(return_value=result)
    mock_db.commit = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db


# ── _wilson_ci ────────────────────────────────────────────────────────────────


def test_wilson_ci_zero_n():
    from routers.admin import _wilson_ci

    lo, hi = _wilson_ci(0, 0)
    assert lo == 0.0
    assert hi == 100.0


def test_wilson_ci_all_wins():
    from routers.admin import _wilson_ci

    lo, hi = _wilson_ci(100, 100)
    assert lo > 90.0
    assert hi == 100.0


def test_wilson_ci_half():
    from routers.admin import _wilson_ci

    lo, hi = _wilson_ci(50, 100)
    assert 40 < lo < 60
    assert 40 < hi < 60
    assert lo < hi


def test_wilson_ci_no_wins():
    from routers.admin import _wilson_ci

    lo, hi = _wilson_ci(0, 100)
    assert lo == 0.0
    assert hi < 10.0


def test_wilson_ci_small_sample():
    from routers.admin import _wilson_ci

    lo, hi = _wilson_ci(3, 5)
    assert 0 <= lo <= 100
    assert lo <= hi <= 100


# ── _find_flagged ─────────────────────────────────────────────────────────────


def test_find_flagged_empty():
    from routers.admin import _find_flagged

    assert _find_flagged({}) == []


def test_find_flagged_no_flags():
    from routers.admin import _find_flagged

    d = {"metric": {"value": 5, "flag": False}}
    assert _find_flagged(d) == []


def test_find_flagged_single_flag():
    from routers.admin import _find_flagged

    d = {"wr": {"value": 0.42, "flag": True, "before": 0.50, "after": 0.42, "delta": -0.08, "delta_pct": -16.0}}
    result = _find_flagged(d)
    assert len(result) == 1
    assert result[0]["metric"] == "wr"
    assert result[0]["before"] == 0.50


def test_find_flagged_nested():
    from routers.admin import _find_flagged

    d = {"section1": {"sub": {"flag": True, "before": 1, "after": 2, "delta": 1, "delta_pct": 100.0}}}
    result = _find_flagged(d)
    assert len(result) == 1
    assert result[0]["metric"] == "section1.sub"


def test_find_flagged_multiple():
    from routers.admin import _find_flagged

    d = {
        "a": {"flag": True, "before": 1, "after": 2, "delta": 1, "delta_pct": 50.0},
        "b": {"flag": False},
        "c": {"flag": True, "before": 5, "after": 3, "delta": -2, "delta_pct": -40.0},
    }
    result = _find_flagged(d)
    assert len(result) == 2
    metrics = {r["metric"] for r in result}
    assert "a" in metrics
    assert "c" in metrics


# ── GET /api/admin/live-wr-stats ──────────────────────────────────────────────


def test_live_wr_stats_no_signals():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals=[])
    app.dependency_overrides[get_current_user] = _make_owner

    with TestClient(app) as client:
        resp = client.get("/api/admin/live-wr-stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall" in data
    assert data["overall"]["n"] == 0


def test_live_wr_stats_with_signals():
    from models import Signal
    from datetime import datetime, timezone

    app = _make_app()

    sig1 = MagicMock(spec=Signal)
    sig1.outcome_pct = 0.8
    sig1.is_sent = True
    sig1.created_at = datetime(2026, 4, 1, tzinfo=timezone.utc).replace(tzinfo=None)

    sig2 = MagicMock(spec=Signal)
    sig2.outcome_pct = -0.3
    sig2.is_sent = True
    sig2.created_at = datetime(2026, 4, 2, tzinfo=timezone.utc).replace(tzinfo=None)

    mock_db = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [sig1, sig2]
    mock_db.execute = AsyncMock(return_value=result)

    async def _get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _make_owner

    with TestClient(app) as client:
        resp = client.get("/api/admin/live-wr-stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall"]["n"] == 2


# ── GET /api/admin/users ──────────────────────────────────────────────────────


def test_list_users_non_owner():
    app = _make_app()
    non_owner = User(id=2, email="u@t.com", is_owner=False, subscription_tier="free", subscription_status="active")
    app.dependency_overrides[get_db] = _mock_db()
    app.dependency_overrides[get_current_user] = lambda: non_owner

    with TestClient(app) as client:
        resp = client.get("/api/admin/users")
    assert resp.status_code == 403


def test_list_users_owner():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals=[])
    app.dependency_overrides[get_current_user] = _make_owner

    with TestClient(app) as client:
        resp = client.get("/api/admin/users")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
