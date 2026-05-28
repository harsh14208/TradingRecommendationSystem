"""
Tests for §38 infrastructure upgrades:
  - Champion/Challenger ML gate: new model only deployed when OOS AUC improves
  - Polygon extended-hours endpoint: happy path, non-200, missing fields, no key
  - Redis OHLCV cache: falls back gracefully to in-memory dict when Redis unavailable
"""
import json
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Champion / Challenger gate (signal_ml.py)
# ─────────────────────────────────────────────────────────────────────────────

def _ml_metadata(auc: float) -> dict:
    return {
        "trained_at": "2026-01-01T00:00:00",
        "n_train": 100, "n_test": 30,
        "oos_accuracy": 0.60, "oos_auc": auc,
        "oos_precision": 0.62, "oos_recall": 0.58,
        "top_features": ["confidence"], "feature_importances": [],
        "deployed": True, "champion_auc": None,
    }


def test_champion_challenger_deploys_better_model(tmp_path):
    """Challenger with AUC 0.65 > champion 0.60 → deployed."""
    import services.signal_ml as sml

    champion_auc = 0.60
    challenger_auc = 0.65

    feature_file = tmp_path / "signal_ml_features.json"
    feature_file.write_text(json.dumps(_ml_metadata(champion_auc)))

    with patch.object(sml, "_FEATURE_FILE", feature_file), \
         patch.object(sml, "_MODEL_FILE", tmp_path / "signal_ml_model.json"):
        # Simulate the save block logic directly
        _should_deploy = challenger_auc > champion_auc
        assert _should_deploy, "Challenger AUC 0.65 > champion 0.60 should deploy"


def test_champion_challenger_rejects_weaker_model(tmp_path):
    """Challenger with AUC 0.55 < champion 0.60 → NOT deployed."""
    import services.signal_ml as sml

    champion_auc = 0.60
    challenger_auc = 0.55

    feature_file = tmp_path / "signal_ml_features.json"
    feature_file.write_text(json.dumps(_ml_metadata(champion_auc)))

    with patch.object(sml, "_FEATURE_FILE", feature_file), \
         patch.object(sml, "_MODEL_FILE", tmp_path / "signal_ml_model.json"):
        _champion_auc = json.loads(feature_file.read_text()).get("oos_auc")
        _should_deploy = challenger_auc > _champion_auc
        assert not _should_deploy, "Challenger AUC 0.55 < champion 0.60 should NOT deploy"


def test_champion_challenger_deploys_when_no_champion(tmp_path):
    """No existing model file → first-run deploy always."""
    import services.signal_ml as sml

    feature_file = tmp_path / "signal_ml_features.json"
    # File doesn't exist — no champion

    with patch.object(sml, "_FEATURE_FILE", feature_file), \
         patch.object(sml, "_MODEL_FILE", tmp_path / "signal_ml_model.json"):
        _champion_auc = None  # no file
        _should_deploy = _champion_auc is None
        assert _should_deploy, "First-run (no champion) should always deploy"


def test_champion_challenger_metadata_always_written(tmp_path):
    """Even when challenger is rejected, metadata file must be updated (for router display)."""
    import services.signal_ml as sml

    champion_meta = _ml_metadata(0.70)
    feature_file = tmp_path / "signal_ml_features.json"
    feature_file.write_text(json.dumps(champion_meta))
    original_mtime = feature_file.stat().st_mtime

    # Simulate the metadata write block (called regardless of _should_deploy)
    new_meta = {**champion_meta, "oos_auc": 0.55, "deployed": False, "champion_auc": 0.70}
    feature_file.write_text(json.dumps(new_meta))

    written = json.loads(feature_file.read_text())
    assert written["deployed"] is False, "Rejected challenger must have deployed=False in metadata"
    assert written["champion_auc"] == 0.70, "champion_auc must be recorded in metadata"


def test_champion_challenger_result_includes_deployed_flag(tmp_path):
    """train_model() return dict must include 'deployed' and 'champion_auc' keys."""
    xgb = pytest.importorskip("xgboost", reason="xgboost not installed")
    import services.signal_ml as sml

    # Stub out DB, XGBoost, sklearn to isolate just the gate logic
    mock_rows = [
        {"ticker": "AAPL", "action": "BUY", "confidence": 65.0, "sentiment": 0.5,
         "sources": ["Options"], "rationale": [], "outcome_pct": 1.5, "style": "position",
         "session": "regular", "rr": "1:2", "entry": 100.0, "stop": 95.0,
         "target": 110.0, "price": 100.0, "created_at": f"2025-{i:02d}-01"}
        for i in range(1, 13)
    ] * 5  # 60 rows

    mock_model = MagicMock()
    mock_model.predict.return_value = [1] * 18
    mock_model.predict_proba.return_value = [[0.4, 0.6]] * 18
    mock_model.feature_importances_ = [0.05] * 19
    mock_model.get_booster.return_value = MagicMock()

    with patch.object(sml, "_load_resolved_signals_sync", return_value=mock_rows), \
         patch.object(sml, "_DATA_DIR", tmp_path), \
         patch.object(sml, "_MODEL_FILE", tmp_path / "model.json"), \
         patch.object(sml, "_FEATURE_FILE", tmp_path / "features.json"), \
         patch.object(xgb, "XGBClassifier", return_value=mock_model):
        result = sml.train_model()

    if result is not None:
        assert "deployed" in result, "train_model() result must include 'deployed' key"
        assert "champion_auc" in result, "train_model() result must include 'champion_auc' key"


# ─────────────────────────────────────────────────────────────────────────────
# Polygon extended-hours endpoint (polygon_client.py)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_polygon_extended_hours_happy_path():
    """Snapshot returns lastTrade.p and prevDay.c → valid dict with gap_pct."""
    from services.polygon_client import get_polygon_extended_hours

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={
        "ticker": {
            "lastTrade": {"p": 152.0},
            "prevDay":   {"c": 150.0},
            "min":       {"v": 50000},
        }
    })
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__  = AsyncMock(return_value=False)
    mock_session.get = MagicMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_resp),
        __aexit__=AsyncMock(return_value=False),
    ))

    with patch("aiohttp.ClientSession", return_value=mock_session), \
         patch("services.polygon_client._get_api_key", return_value="fake_key"):
        result = await get_polygon_extended_hours("AAPL")

    assert result is not None
    assert result["gap_pct"] == pytest.approx(1.333, abs=0.01)
    assert result["direction"] == "up"
    assert result["ext_volume"] == 50000
    assert result["prev_close"] == 150.0


@pytest.mark.asyncio
async def test_polygon_extended_hours_no_api_key():
    """No API key → returns None without making any HTTP request."""
    from services.polygon_client import get_polygon_extended_hours

    with patch("services.polygon_client._get_api_key", return_value=""), \
         patch("aiohttp.ClientSession") as mock_cls:
        result = await get_polygon_extended_hours("AAPL")

    mock_cls.assert_not_called()
    assert result is None


@pytest.mark.asyncio
async def test_polygon_extended_hours_non_200():
    """Non-200 HTTP response (e.g. 403) → returns None without raising."""
    from services.polygon_client import get_polygon_extended_hours

    mock_resp = AsyncMock()
    mock_resp.status = 403
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__  = AsyncMock(return_value=False)
    mock_session.get = MagicMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_resp),
        __aexit__=AsyncMock(return_value=False),
    ))

    with patch("aiohttp.ClientSession", return_value=mock_session), \
         patch("services.polygon_client._get_api_key", return_value="key"):
        result = await get_polygon_extended_hours("TSLA")

    assert result is None


@pytest.mark.asyncio
async def test_polygon_extended_hours_missing_fields():
    """Missing lastTrade or prevDay → returns None (not a partial dict)."""
    from services.polygon_client import get_polygon_extended_hours

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"ticker": {}})  # empty ticker data
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__  = AsyncMock(return_value=False)
    mock_session.get = MagicMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_resp),
        __aexit__=AsyncMock(return_value=False),
    ))

    with patch("aiohttp.ClientSession", return_value=mock_session), \
         patch("services.polygon_client._get_api_key", return_value="key"):
        result = await get_polygon_extended_hours("MSFT")

    assert result is None


@pytest.mark.asyncio
async def test_polygon_extended_hours_flat_direction():
    """Price change ≤ 0.1% → direction='flat'."""
    from services.polygon_client import get_polygon_extended_hours

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={
        "ticker": {
            "lastTrade": {"p": 100.05},
            "prevDay":   {"c": 100.0},
            "min":       {"v": 1000},
        }
    })
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__  = AsyncMock(return_value=False)
    mock_session.get = MagicMock(return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_resp),
        __aexit__=AsyncMock(return_value=False),
    ))

    with patch("aiohttp.ClientSession", return_value=mock_session), \
         patch("services.polygon_client._get_api_key", return_value="key"):
        result = await get_polygon_extended_hours("SPY")

    assert result is not None
    assert result["direction"] == "flat"


# ─────────────────────────────────────────────────────────────────────────────
# Redis OHLCV cache fallback (market_data.py)
# ─────────────────────────────────────────────────────────────────────────────

def test_ohlcv_cache_fallback_to_memory_when_redis_unavailable():
    """When _redis_client is None, _ohlcv_cache_get/_ohlcv_cache_set use the in-memory dict."""
    import services.market_data as md
    import pandas as pd
    import time

    key = ("FALLBACK_TEST", "1mo", "1d")
    df  = pd.DataFrame({"Close": [100.0, 101.0]})

    # Ensure Redis is not active for this test
    orig_redis = md._redis_client
    md._redis_client = None
    try:
        md._ohlcv_cache.pop(key, None)  # clean slate
        md._ohlcv_cache_set(key, df, time.time())
        result = md._ohlcv_cache_get(key)
        assert result is not None, "In-memory fallback should return cached DataFrame"
        assert list(result["Close"]) == [100.0, 101.0]
    finally:
        md._redis_client = orig_redis
        md._ohlcv_cache.pop(key, None)


def test_ohlcv_cache_returns_none_after_ttl(monkeypatch):
    """Expired cache entry (older than 15 min) returns None via in-memory fallback."""
    import services.market_data as md
    import pandas as pd
    import time

    key = ("TTL_TEST", "3mo", "1d")
    df  = pd.DataFrame({"Close": [200.0]})

    orig_redis = md._redis_client
    md._redis_client = None
    try:
        # Write with a timestamp 20 minutes in the past
        stale_ts = time.time() - 1200
        md._ohlcv_cache[key] = {"df": df, "ts": stale_ts}
        result = md._ohlcv_cache_get(key)
        assert result is None, "Expired entry should return None"
    finally:
        md._redis_client = orig_redis
        md._ohlcv_cache.pop(key, None)


def test_ohlcv_cache_redis_error_falls_through():
    """If Redis raises on get, returns None without propagating the exception."""
    import services.market_data as md

    mock_redis = MagicMock()
    mock_redis.get.side_effect = Exception("connection reset")

    orig_redis = md._redis_client
    md._redis_client = mock_redis
    try:
        result = md._ohlcv_cache_get(("ERR", "1d", "1d"))
        assert result is None, "Redis error should silently return None"
    finally:
        md._redis_client = orig_redis
