"""Tests for routers/accuracy.py — source and ticker accuracy endpoints."""

import json
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import Signal, User
from services.auth_svc import get_current_user


def _make_app():
    from routers.accuracy import router

    app = FastAPI()
    app.include_router(router)

    def _user():
        return User(id=1, email="t@t.com", is_owner=True, subscription_tier="pro")

    app.dependency_overrides[get_current_user] = _user
    return app


def _mock_db(signals):
    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = signals

    async def _get_db():
        mock_db.execute = AsyncMock(return_value=mock_result)
        yield mock_db

    return _get_db


def _make_signal(outcome, sources):
    s = MagicMock(spec=Signal)
    s.outcome_pct = outcome
    s.outcome_3d = None
    s.outcome_1d = None
    s.outcome_14d = None
    s.is_sent = True
    s.sources = sources
    s.ticker = "AAPL"
    return s


def test_source_accuracy_empty():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([])
    with TestClient(app) as client:
        resp = client.get("/api/accuracy/sources")
    assert resp.status_code == 200
    assert resp.json() == []


def test_source_accuracy_with_data():
    signals = [
        _make_signal(2.0, ["RSI", "MACD"]),
        _make_signal(-1.0, ["RSI"]),
        _make_signal(1.5, ["RSI"]),
        _make_signal(None, ["RSI"]),  # no outcome — should be skipped
    ]
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals)
    with TestClient(app) as client:
        resp = client.get("/api/accuracy/sources")
    assert resp.status_code == 200
    data = resp.json()
    # RSI has 3 signals (>= 3 threshold)
    sources = [d["source"] for d in data]
    assert "RSI" in sources
    rsi = next(d for d in data if d["source"] == "RSI")
    assert rsi["total"] == 3
    assert rsi["wins"] == 2


def test_source_accuracy_json_sources():
    # Test sources stored as JSON string
    s = MagicMock(spec=Signal)
    s.outcome_pct = 1.0
    s.outcome_3d = None
    s.outcome_1d = None
    s.outcome_14d = None
    s.is_sent = True
    s.sources = json.dumps(["BB", "VWAP"])
    s.ticker = "NVDA"

    signals = [s] * 4  # 4 to exceed threshold
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals)
    with TestClient(app) as client:
        resp = client.get("/api/accuracy/sources")
    assert resp.status_code == 200


def test_ticker_accuracy_empty():
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db([])
    with TestClient(app) as client:
        resp = client.get("/api/accuracy/tickers")
    assert resp.status_code == 200
    assert resp.json() == []


def test_ticker_accuracy_with_data():
    signals = [
        _make_signal(3.0, ["BB"]),
        _make_signal(-0.5, ["BB"]),
        _make_signal(1.0, ["RSI"]),
    ]
    app = _make_app()
    app.dependency_overrides[get_db] = _mock_db(signals)
    with TestClient(app) as client:
        resp = client.get("/api/accuracy/tickers")
    assert resp.status_code == 200
    data = resp.json()
    # AAPL should appear (≥ 2 signals)
    tickers = [d["ticker"] for d in data]
    assert "AAPL" in tickers
    aapl = next(d for d in data if d["ticker"] == "AAPL")
    assert aapl["total"] == 3
    assert "win_rate" in aapl
    assert "top_sources" in aapl
