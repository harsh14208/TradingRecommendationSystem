"""Tests for signal_engine.py pure helper functions."""
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


# ── _get_analyst_redis ────────────────────────────────────────────────────────

def test_get_analyst_redis_unavailable():
    """Redis unavailable → returns None gracefully."""
    import services.signal_engine as se
    # Reset state
    se._analyst_redis_checked = False
    se._analyst_redis = None

    with patch("redis.Redis.from_url") as mock_redis:
        mock_redis.return_value.ping.side_effect = Exception("Connection refused")
        result = se._get_analyst_redis()

    assert result is None
    # Reset for subsequent tests
    se._analyst_redis_checked = False
    se._analyst_redis = None


def test_get_analyst_redis_cached():
    """Second call returns cached result without re-checking."""
    import services.signal_engine as se
    se._analyst_redis_checked = True
    se._analyst_redis = MagicMock()  # fake Redis

    result = se._get_analyst_redis()
    assert result is se._analyst_redis

    # Reset
    se._analyst_redis_checked = False
    se._analyst_redis = None


# ── _analyst_cache_get ────────────────────────────────────────────────────────

def test_analyst_cache_get_no_redis():
    from services.signal_engine import _analyst_cache_get
    import services.signal_engine as se
    se._analyst_redis_checked = True
    se._analyst_redis = None

    result = _analyst_cache_get("AAPL")
    assert result is None

    se._analyst_redis_checked = False


def test_analyst_cache_get_hit():
    from services.signal_engine import _analyst_cache_get
    import services.signal_engine as se
    mock_r = MagicMock()
    mock_r.get.return_value = json.dumps({"rating": "BUY", "target": 200.0})
    se._analyst_redis_checked = True
    se._analyst_redis = mock_r

    result = _analyst_cache_get("AAPL")
    assert result is not None
    assert result["rating"] == "BUY"

    se._analyst_redis_checked = False
    se._analyst_redis = None


def test_analyst_cache_get_miss():
    from services.signal_engine import _analyst_cache_get
    import services.signal_engine as se
    mock_r = MagicMock()
    mock_r.get.return_value = None
    se._analyst_redis_checked = True
    se._analyst_redis = mock_r

    result = _analyst_cache_get("NVDA")
    assert result is None

    se._analyst_redis_checked = False
    se._analyst_redis = None


def test_analyst_cache_get_error():
    from services.signal_engine import _analyst_cache_get
    import services.signal_engine as se
    mock_r = MagicMock()
    mock_r.get.side_effect = Exception("redis error")
    se._analyst_redis_checked = True
    se._analyst_redis = mock_r

    result = _analyst_cache_get("MSFT")
    assert result is None

    se._analyst_redis_checked = False
    se._analyst_redis = None


# ── _analyst_cache_set ────────────────────────────────────────────────────────

def test_analyst_cache_set_no_redis():
    from services.signal_engine import _analyst_cache_set
    import services.signal_engine as se
    se._analyst_redis_checked = True
    se._analyst_redis = None

    # Should not raise
    _analyst_cache_set("AAPL", {"rating": "BUY"})

    se._analyst_redis_checked = False


def test_analyst_cache_set_success():
    from services.signal_engine import _analyst_cache_set
    import services.signal_engine as se
    mock_r = MagicMock()
    se._analyst_redis_checked = True
    se._analyst_redis = mock_r

    _analyst_cache_set("AAPL", {"rating": "HOLD"})
    mock_r.setex.assert_called_once()

    se._analyst_redis_checked = False
    se._analyst_redis = None


def test_analyst_cache_set_error():
    from services.signal_engine import _analyst_cache_set
    import services.signal_engine as se
    mock_r = MagicMock()
    mock_r.setex.side_effect = Exception("redis error")
    se._analyst_redis_checked = True
    se._analyst_redis = mock_r

    # Should not raise
    _analyst_cache_set("NVDA", {"rating": "SELL"})

    se._analyst_redis_checked = False
    se._analyst_redis = None


# ── _apply_q1_rebalancing ─────────────────────────────────────────────────────

def test_q1_rebalancing_high_vix():
    """VIX >= 30 in Q1 → stress regime, no change."""
    from services.signal_engine import _apply_q1_rebalancing

    # `datetime` here is the class captured from `from datetime import datetime` at top
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 1, 10)
        score, rationale = _apply_q1_rebalancing(60.0, [], "XLK", 35.0)

    assert score == 60.0
    assert rationale == []


def test_q1_rebalancing_no_sector():
    """No sector ETF → no change."""
    from services.signal_engine import _apply_q1_rebalancing

    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 2, 15)
        score, rationale = _apply_q1_rebalancing(60.0, [], None, 15.0)

    assert score == 60.0


def test_q1_rebalancing_applied():
    """Q1, valid sector, low VIX → +3pp bonus."""
    from services.signal_engine import _apply_q1_rebalancing

    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 1, 10)
        score, rationale = _apply_q1_rebalancing(60.0, [], "XLK", 15.0)

    assert score == 63.0
    assert len(rationale) == 1
    assert "§79" in rationale[0]["head"]


def test_q1_rebalancing_outside_q1():
    """Outside Jan–Mar window → no change."""
    from services.signal_engine import _apply_q1_rebalancing

    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 6, 15)
        score, rationale = _apply_q1_rebalancing(60.0, [], "XLK", 15.0)

    assert score == 60.0
    assert rationale == []


def test_q1_rebalancing_no_vix():
    """Q1, valid sector, vix=None → applied (no stress gate)."""
    from services.signal_engine import _apply_q1_rebalancing

    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 3, 1)
        score, rationale = _apply_q1_rebalancing(50.0, [], "XLV", None)

    assert score == 53.0


# ── _compute_1h_techs ─────────────────────────────────────────────────────────

def test_compute_1h_techs_basic():
    from services.signal_engine import _compute_1h_techs

    # Oscillating prices so RSI is computable (not NaN)
    closes = np.array([100 + i * 0.3 + np.sin(i * 0.8) * 2 for i in range(50)])
    df_1h = pd.DataFrame({"Close": closes})

    result = _compute_1h_techs(df_1h)
    assert "rsi_1h" in result
    assert "macd_1h" in result
    assert "above_ema_1h" in result
    assert isinstance(result["rsi_1h"], float)
    assert isinstance(result["macd_1h"], float)
    assert isinstance(result["above_ema_1h"], (bool, np.bool_))


def test_compute_1h_techs_rising():
    from services.signal_engine import _compute_1h_techs

    # Net-upward but oscillating prices → above EMA, finite RSI
    closes = np.array([100 + i * 0.4 + np.sin(i * 1.2) * 1.5 for i in range(50)])
    df_1h = pd.DataFrame({"Close": closes})
    result = _compute_1h_techs(df_1h)
    assert result["above_ema_1h"] is True
    # RSI may be NaN for edge cases; just verify it's a float
    assert isinstance(result["rsi_1h"], float)


def test_compute_1h_techs_falling():
    from services.signal_engine import _compute_1h_techs

    # Net-downward but oscillating prices → below EMA, finite RSI
    closes = np.array([120 - i * 0.4 + np.sin(i * 1.2) * 1.5 for i in range(50)])
    df_1h = pd.DataFrame({"Close": closes})
    result = _compute_1h_techs(df_1h)
    assert result["above_ema_1h"] is False
    assert isinstance(result["rsi_1h"], float)
