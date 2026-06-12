"""Tests for routers/public.py — unauthenticated track record endpoint."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import Signal
import pytest


@pytest.fixture(autouse=True)
def _clear_public_cache():
    from routers.public import _clear_track_record_cache

    _clear_track_record_cache()


def _make_app():
    from routers.public import router

    app = FastAPI()
    app.include_router(router)
    return app


def _mock_signal(
    ticker="AAPL", action="BUY", confidence=75, outcome_1d=2.0, outcome_pct=None, created_at=None, sources=None
):
    s = MagicMock(spec=Signal)
    s.ticker = ticker
    s.action = action
    s.confidence = confidence
    s.is_sent = True
    s.outcome_1d = outcome_1d
    s.outcome_pct = outcome_pct
    s.outcome_3d = None
    s.outcome_14d = None
    s.created_at = created_at or datetime(2026, 1, 15, 10, 0, 0)
    s.sources = sources or ["RSI", "BB"]
    return s


def _mock_db(signals):
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = signals
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def _get_db():
        yield mock_db

    return _get_db


def test_track_record_no_data():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([])
    with TestClient(app) as client:
        resp = client.get("/api/public/track-record")
    assert resp.status_code == 200
    assert resp.json()["no_data"] is True


def test_track_record_with_signals():
    signals = [
        _mock_signal("AAPL", "BUY", 80, outcome_1d=2.5, created_at=datetime(2026, 3, 1)),
        _mock_signal("NVDA", "BUY", 75, outcome_1d=-1.0, created_at=datetime(2026, 3, 5)),
        _mock_signal("TSLA", "SELL", 70, outcome_1d=1.5, created_at=datetime(2026, 2, 15)),
    ]
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals)
    with TestClient(app) as client:
        resp = client.get("/api/public/track-record")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall" in data
    assert data["overall"]["n"] == 3
    assert "by_action" in data
    assert "top_tickers" in data
    assert "top_signals" in data


def test_track_record_overall_stats():
    # 4 signals: 3 wins, 1 loss
    signals = [
        _mock_signal("AAPL", "BUY", 80, outcome_1d=3.0, created_at=datetime(2026, 3, 1)),
        _mock_signal("NVDA", "BUY", 75, outcome_1d=2.0, created_at=datetime(2026, 3, 2)),
        _mock_signal("AMD", "BUY", 70, outcome_1d=1.0, created_at=datetime(2026, 3, 3)),
        _mock_signal("TSLA", "BUY", 65, outcome_1d=-2.0, created_at=datetime(2026, 3, 4)),
    ]
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals)
    with TestClient(app) as client:
        resp = client.get("/api/public/track-record")
    assert resp.status_code == 200
    overall = resp.json()["overall"]
    assert overall["win_rate"] == 75.0
    assert overall["n"] == 4


def test_track_record_by_month():
    signals = [
        _mock_signal("AAPL", "BUY", 80, outcome_1d=2.0, created_at=datetime(2026, 1, 10)),
        _mock_signal("NVDA", "BUY", 75, outcome_1d=1.5, created_at=datetime(2026, 1, 15)),
        _mock_signal("AMD", "BUY", 70, outcome_1d=-1.0, created_at=datetime(2026, 2, 5)),
    ]
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals)
    with TestClient(app) as client:
        resp = client.get("/api/public/track-record")
    data = resp.json()
    assert "by_month" in data
    months = [m["month"] for m in data["by_month"]]
    assert "2026-01" in months


def test_track_record_outcome_pct_used():
    # outcome_pct takes priority over outcome_1d
    s = _mock_signal("AAPL", "BUY", 80, outcome_1d=None)
    s.outcome_pct = 5.0
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([s])
    with TestClient(app) as client:
        resp = client.get("/api/public/track-record")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall"]["n"] == 1
    assert data["overall"]["win_rate"] == 100.0
