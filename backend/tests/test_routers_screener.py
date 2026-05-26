"""
Tests for /api/screener endpoints:
  GET    /api/screener          — list presets
  POST   /api/screener          — create/replace preset
  DELETE /api/screener/{name}   — delete preset
  GET    /api/screener/{name}/run — run preset against live signals
  POST   /api/screener/preview  — preview without saving
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from models import User, AppSettings, Signal
from database import get_db
from services.auth_svc import get_current_user
from routers.screener import router, apply_screener, FilterRule


# ── Helper ────────────────────────────────────────────────────────────────────

def _app(db=None):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="u@x.com", is_owner=False)
    if db is not None:
        async def _db():
            yield db
        app.dependency_overrides[get_db] = _db
    return app


def _settings_row(screeners: dict) -> MagicMock:
    row = MagicMock(spec=AppSettings)
    row.data = {"screeners": screeners}
    return row


def _mock_db(screeners: dict):
    db = AsyncMock()
    row = _settings_row(screeners)
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=row)))
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


# ── apply_screener unit tests ─────────────────────────────────────────────────

def _rule(**kw) -> FilterRule:
    return FilterRule(**kw)


def test_apply_screener_confidence_gte():
    sigs = [{"confidence": 80}, {"confidence": 60}, {"confidence": 75}]
    out = apply_screener(sigs, [_rule(field="confidence", op="gte", value=75)])
    assert len(out) == 2
    assert all(s["confidence"] >= 75 for s in out)


def test_apply_screener_action_eq():
    sigs = [{"action": "BUY"}, {"action": "SELL"}, {"action": "BUY"}]
    out = apply_screener(sigs, [_rule(field="action", op="eq", value="BUY")])
    assert len(out) == 2


def test_apply_screener_has_source():
    sigs = [
        {"sources": ["news", "technical"]},
        {"sources": ["technical"]},
        {"sources": ["news"]},
    ]
    out = apply_screener(sigs, [_rule(field="has_source", op="eq", value="news")])
    assert len(out) == 2


def test_apply_screener_multi_rule_and():
    sigs = [
        {"confidence": 80, "action": "BUY"},
        {"confidence": 80, "action": "SELL"},
        {"confidence": 60, "action": "BUY"},
    ]
    out = apply_screener(sigs, [
        _rule(field="confidence", op="gte", value=75),
        _rule(field="action", op="eq", value="BUY"),
    ])
    assert len(out) == 1
    assert out[0]["confidence"] == 80 and out[0]["action"] == "BUY"


def test_apply_screener_in_operator():
    sigs = [{"action": "BUY"}, {"action": "SELL"}, {"action": "HOLD"}]
    out = apply_screener(sigs, [_rule(field="action", op="in", value=["BUY", "SELL"])])
    assert len(out) == 2


def test_apply_screener_contains():
    sigs = [{"ticker": "AAPL"}, {"ticker": "MSFT"}, {"ticker": "GOOGL"}]
    out = apply_screener(sigs, [_rule(field="ticker", op="contains", value="OOG")])
    assert len(out) == 1 and out[0]["ticker"] == "GOOGL"


# ── List screeners ────────────────────────────────────────────────────────────

def test_list_screeners_empty():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.get("/api/screener")
    assert res.status_code == 200
    assert res.json() == []


def test_list_screeners_returns_presets():
    presets = {
        "High Conf": [{"field": "confidence", "op": "gte", "value": 80}],
        "BUY only":  [{"field": "action", "op": "eq", "value": "BUY"}],
    }
    db = _mock_db(presets)
    with TestClient(_app(db)) as c:
        res = c.get("/api/screener")
    assert res.status_code == 200
    data = res.json()
    names = [p["name"] for p in data]
    assert "High Conf" in names and "BUY only" in names


# ── Create screener ───────────────────────────────────────────────────────────

def test_create_screener_success():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={
            "name": "My Screener",
            "rules": [{"field": "confidence", "op": "gte", "value": 75}],
        })
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "My Screener"
    assert len(data["rules"]) == 1
    db.commit.assert_awaited()


def test_create_screener_empty_rules_422():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={"name": "Empty", "rules": []})
    assert res.status_code == 422


def test_create_screener_invalid_field_422():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={
            "name": "Bad",
            "rules": [{"field": "invalid_field", "op": "eq", "value": "x"}],
        })
    assert res.status_code == 422


def test_create_screener_invalid_op_422():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={
            "name": "Bad",
            "rules": [{"field": "confidence", "op": "between", "value": 75}],
        })
    assert res.status_code == 422


def test_create_screener_invalid_name_422():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={
            "name": "!@#$%^invalid",
            "rules": [{"field": "confidence", "op": "gte", "value": 75}],
        })
    assert res.status_code == 422


def test_create_screener_at_limit_returns_400():
    # 20 existing screeners + trying to add a new one → 400
    existing = {f"s{i}": [{"field": "confidence", "op": "gte", "value": i}] for i in range(20)}
    db = _mock_db(existing)
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={
            "name": "New One",
            "rules": [{"field": "confidence", "op": "gte", "value": 80}],
        })
    assert res.status_code == 400


def test_create_screener_replace_existing_ok():
    # replacing an existing screener (same name) doesn't count against limit
    existing = {f"s{i}": [{"field": "confidence", "op": "gte", "value": i}] for i in range(20)}
    db = _mock_db(existing)
    with TestClient(_app(db)) as c:
        res = c.post("/api/screener", json={
            "name": "s0",
            "rules": [{"field": "confidence", "op": "gte", "value": 90}],
        })
    assert res.status_code == 200


# ── Delete screener ───────────────────────────────────────────────────────────

def test_delete_screener_success():
    presets = {"My Screener": [{"field": "confidence", "op": "gte", "value": 75}]}
    db = _mock_db(presets)
    with TestClient(_app(db)) as c:
        res = c.delete("/api/screener/My%20Screener")
    assert res.status_code == 200
    assert res.json()["deleted"] == "My Screener"
    db.commit.assert_awaited()


def test_delete_screener_not_found_404():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.delete("/api/screener/nonexistent")
    assert res.status_code == 404


# ── Preview ───────────────────────────────────────────────────────────────────

def _mock_signal_row(id, ticker, action, confidence, sentiment=0, style="swing", rr="2.0", sources=None):
    sig = MagicMock(spec=Signal)
    sig.id         = id
    sig.ticker     = ticker
    sig.action     = action
    sig.confidence = confidence
    sig.sentiment  = sentiment
    sig.style      = style
    sig.rr         = rr
    sig.price      = 100.0
    sig.sources    = sources or []
    sig.headline   = "test"
    sig.created_at = datetime(2024, 1, 1)
    sig.is_active  = True
    return sig


def test_preview_screener_returns_matching():
    sig1 = _mock_signal_row(1, "AAPL", "BUY", 85)
    sig2 = _mock_signal_row(2, "MSFT", "SELL", 60)
    sig3 = _mock_signal_row(3, "GOOGL", "BUY", 78)

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [sig1, sig2, sig3]
    # preview uses db.execute for signals, then _load_screeners uses db.execute for AppSettings
    # We set up execute to handle both calls
    settings_mock = MagicMock()
    settings_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(side_effect=[result_mock, settings_mock])

    with TestClient(_app(db)) as c:
        res = c.post("/api/screener/preview", json={
            "name": "Test",
            "rules": [{"field": "confidence", "op": "gte", "value": 75}],
        })
    assert res.status_code == 200
    data = res.json()
    assert data["matched"] == 2
    tickers = [s["ticker"] for s in data["signals"]]
    assert "AAPL" in tickers and "GOOGL" in tickers
    assert "MSFT" not in tickers


# ── Run saved screener ────────────────────────────────────────────────────────

def test_run_screener_not_found_404():
    db = _mock_db({})
    with TestClient(_app(db)) as c:
        res = c.get("/api/screener/nonexistent/run")
    assert res.status_code == 404


def test_run_screener_returns_results():
    presets = {"High Conf": [{"field": "confidence", "op": "gte", "value": 80}]}
    sig1 = _mock_signal_row(1, "AAPL", "BUY", 85)
    sig2 = _mock_signal_row(2, "TSLA", "BUY", 72)

    db = AsyncMock()
    settings_row = _settings_row(presets)
    signals_result = MagicMock()
    signals_result.scalars.return_value.all.return_value = [sig1, sig2]

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalar_one_or_none=MagicMock(return_value=settings_row)),  # load presets
        signals_result,  # fetch signals
    ])

    with TestClient(_app(db)) as c:
        res = c.get("/api/screener/High%20Conf/run")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "High Conf"
    assert data["matched"] == 1
    assert data["signals"][0]["ticker"] == "AAPL"
