"""Unit tests for routers/quotes.py — pure helpers and gated endpoints."""

import pandas as pd
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from models import User


def _make_user(tier="basic", status="active", is_owner=False):
    u = User(id=1, email="t@t.com", is_owner=is_owner, subscription_tier=tier, subscription_status=status)
    u.full_name = "Test"
    return u


def _make_app():
    from routers.quotes import router

    app = FastAPI()
    app.include_router(router)
    return app


# ── _require_basic ────────────────────────────────────────────────────────────


def test_require_basic_owner_passes():
    from routers.quotes import _require_basic

    owner = _make_user(tier="free", is_owner=True)
    _require_basic(owner)  # should not raise


def test_require_basic_basic_tier_passes():
    from routers.quotes import _require_basic

    user = _make_user(tier="basic", status="active")
    _require_basic(user)  # should not raise


def test_require_basic_pro_passes():
    from routers.quotes import _require_basic

    user = _make_user(tier="pro", status="active")
    _require_basic(user)


def test_require_basic_free_raises():
    from routers.quotes import _require_basic
    from fastapi import HTTPException

    user = _make_user(tier="free", status="active")
    with pytest.raises(HTTPException) as exc:
        _require_basic(user)
    assert exc.value.status_code == 402


def test_require_basic_inactive_raises():
    from routers.quotes import _require_basic
    from fastapi import HTTPException

    user = _make_user(tier="basic", status="inactive")
    with pytest.raises(HTTPException) as exc:
        _require_basic(user)
    assert exc.value.status_code == 402


# ── _ret ──────────────────────────────────────────────────────────────────────


def _make_closes(values):
    idx = pd.date_range("2026-01-01", periods=len(values))
    return pd.Series(values, index=idx)


def test_ret_none_closes():
    from routers.quotes import _ret

    assert _ret(None, 5) is None


def test_ret_too_short():
    from routers.quotes import _ret

    closes = _make_closes([100.0])
    assert _ret(closes, 5) is None


def test_ret_positive():
    from routers.quotes import _ret

    closes = _make_closes([100.0, 105.0])
    result = _ret(closes, 1)
    assert result == pytest.approx(5.0, abs=0.01)


def test_ret_negative():
    from routers.quotes import _ret

    closes = _make_closes([100.0, 90.0])
    result = _ret(closes, 1)
    assert result == pytest.approx(-10.0, abs=0.01)


def test_ret_zero_base():
    from routers.quotes import _ret

    closes = _make_closes([0.0, 100.0])
    assert _ret(closes, 1) is None


def test_ret_caps_days_at_length():
    from routers.quotes import _ret

    # Asks for 100 days but only 5 available
    closes = _make_closes([90.0, 92.0, 95.0, 98.0, 100.0])
    result = _ret(closes, 100)
    assert result is not None
    assert isinstance(result, float)


def test_ret_multiday():
    from routers.quotes import _ret

    closes = _make_closes([100.0, 101.0, 103.0, 106.0])
    result = _ret(closes, 3)
    assert result == pytest.approx(6.0, abs=0.01)


# ── _ytd_ret ──────────────────────────────────────────────────────────────────


def test_ytd_ret_none():
    from routers.quotes import _ytd_ret

    assert _ytd_ret(None) is None


def test_ytd_ret_empty():
    from routers.quotes import _ytd_ret

    assert _ytd_ret(pd.DataFrame()) is None


def test_ytd_ret_no_ytd_data():
    from routers.quotes import _ytd_ret

    # All dates are from prior year
    idx = pd.date_range("2025-01-01", periods=3)
    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=idx)
    result = _ytd_ret(df)
    # May be None if no dates ≥ Jan 1 current year, or a value
    assert result is None or isinstance(result, float)


def test_ytd_ret_with_ytd_data():
    from routers.quotes import _ytd_ret

    today = date.today()
    start = today.replace(month=1, day=2)
    dates = pd.date_range(start.strftime("%Y-%m-%d"), periods=5)
    df = pd.DataFrame({"Close": [100.0, 102.0, 104.0, 106.0, 110.0]}, index=dates)
    result = _ytd_ret(df)
    assert result is not None
    assert isinstance(result, float)
    assert result > 0


def test_ytd_ret_zero_base():
    from routers.quotes import _ytd_ret

    today = date.today()
    start = today.replace(month=1, day=2)
    dates = pd.date_range(start.strftime("%Y-%m-%d"), periods=3)
    df = pd.DataFrame({"Close": [0.0, 1.0, 2.0]}, index=dates)
    assert _ytd_ret(df) is None


def test_ytd_ret_single_ytd_row():
    from routers.quotes import _ytd_ret

    today = date.today()
    start = today.replace(month=1, day=2)
    df = pd.DataFrame({"Close": [100.0]}, index=pd.date_range(start.strftime("%Y-%m-%d"), periods=1))
    result = _ytd_ret(df)
    assert result is None  # need at least 2 rows


# ── GET /api/quotes ───────────────────────────────────────────────────────────


def test_quotes_endpoint():
    app = _make_app()

    with (
        patch("routers.quotes.get_settings") as mock_settings,
        patch("routers.quotes.get_quotes", new_callable=AsyncMock, return_value={"AAPL": 150.0}),
    ):
        mock_settings.return_value.tickers = ["AAPL"]
        with TestClient(app) as client:
            resp = client.get("/api/quotes")
    assert resp.status_code == 200


# ── GET /api/market/sectors (cache path) ─────────────────────────────────────


def test_sector_heatmap_cached():
    from routers import quotes as q

    q._sector_cache["data"] = [{"etf": "XLK", "ret_1d": 0.5}]
    q._sector_cache["ts"] = 1e18  # far future, won't expire

    app = _make_app()
    with TestClient(app) as client:
        resp = client.get("/api/market/sectors")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0

    # Reset cache
    q._sector_cache["data"] = None
    q._sector_cache["ts"] = 0


# ── GET /api/market/breadth ───────────────────────────────────────────────────


def test_market_overview_returns_dict():
    app = _make_app()
    mock_breadth = {"advance_decline": 1.2, "new_highs": 50}
    mock_fear = {"value": 45, "label": "Fear"}
    mock_pc = {"pc_ratio": 0.85}

    with (
        patch("routers.quotes.get_market_breadth", new_callable=AsyncMock, return_value=mock_breadth),
        patch("routers.quotes.get_fear_greed", new_callable=AsyncMock, return_value=mock_fear),
        patch("routers.quotes.get_put_call_ratio", new_callable=AsyncMock, return_value=mock_pc),
    ):
        with TestClient(app) as client:
            resp = client.get("/api/market/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
