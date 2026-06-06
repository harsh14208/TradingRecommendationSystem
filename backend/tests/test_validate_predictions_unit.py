"""Tests for validate_predictions.py — pure helpers and async resolution logic."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


def _import_vp():
    import validate_predictions as vp

    return vp


# ── _pct ──────────────────────────────────────────────────────────────────────


def test_pct_buy_gain():
    vp = _import_vp()
    assert vp._pct(110.0, 100.0, "BUY") == pytest.approx(10.0)


def test_pct_buy_loss():
    vp = _import_vp()
    assert vp._pct(95.0, 100.0, "BUY") == pytest.approx(-5.0)


def test_pct_sell_gain():
    vp = _import_vp()
    # SELL: current < entry = gain (short)
    assert vp._pct(95.0, 100.0, "SELL") == pytest.approx(5.0)


def test_pct_sell_loss():
    vp = _import_vp()
    assert vp._pct(105.0, 100.0, "SELL") == pytest.approx(-5.0)


def test_pct_zero_entry():
    vp = _import_vp()
    assert vp._pct(100.0, 0.0, "BUY") is None


def test_pct_none_inputs():
    vp = _import_vp()
    assert vp._pct(None, 100.0, "BUY") is None
    assert vp._pct(100.0, None, "BUY") is None


# ── _age_days ─────────────────────────────────────────────────────────────────


def test_age_days_recent():
    vp = _import_vp()
    sig = MagicMock()
    sig.created_at = datetime.now(timezone.utc) - timedelta(days=5)
    age = vp._age_days(sig)
    assert 4.9 < age < 5.1


def test_age_days_naive_datetime():
    vp = _import_vp()
    sig = MagicMock()
    sig.created_at = datetime.utcnow() - timedelta(days=10)
    age = vp._age_days(sig)
    assert 9.9 < age < 10.1


def test_age_days_no_created_at():
    vp = _import_vp()
    sig = MagicMock()
    sig.created_at = None
    assert vp._age_days(sig) == 0


# ── _best_outcome ─────────────────────────────────────────────────────────────


def test_best_outcome_prefers_14d():
    vp = _import_vp()
    sig = MagicMock()
    sig.outcome_14d = 3.0
    sig.outcome_pct = 2.0
    sig.outcome_3d = 1.0
    sig.outcome_1d = 0.5
    assert vp._best_outcome(sig) == 3.0


def test_best_outcome_fallback_chain():
    vp = _import_vp()
    sig = MagicMock()
    sig.outcome_14d = None
    sig.outcome_pct = None
    sig.outcome_3d = None
    sig.outcome_1d = 1.5
    assert vp._best_outcome(sig) == 1.5


def test_best_outcome_all_none():
    vp = _import_vp()
    sig = MagicMock()
    sig.outcome_14d = None
    sig.outcome_pct = None
    sig.outcome_3d = None
    sig.outcome_1d = None
    assert vp._best_outcome(sig) is None


# ── _is_win ───────────────────────────────────────────────────────────────────


def test_is_win_target_exit():
    vp = _import_vp()
    sig = MagicMock()
    sig.exit_type = "target"
    assert vp._is_win(sig) is True


def test_is_win_stop_exit():
    vp = _import_vp()
    sig = MagicMock()
    sig.exit_type = "stop"
    assert vp._is_win(sig) is False


def test_is_win_by_outcome():
    vp = _import_vp()
    sig = MagicMock()
    sig.exit_type = None
    sig.outcome_14d = None
    sig.outcome_pct = 2.0  # Above friction
    sig.outcome_3d = None
    sig.outcome_1d = None
    assert vp._is_win(sig) is True


def test_is_not_win_by_outcome():
    vp = _import_vp()
    sig = MagicMock()
    sig.exit_type = None
    sig.outcome_14d = None
    sig.outcome_pct = -1.0
    sig.outcome_3d = None
    sig.outcome_1d = None
    assert vp._is_win(sig) is False


def test_is_not_win_no_outcome():
    vp = _import_vp()
    sig = MagicMock()
    sig.exit_type = None
    sig.outcome_14d = None
    sig.outcome_pct = None
    sig.outcome_3d = None
    sig.outcome_1d = None
    assert vp._is_win(sig) is False


# ── _effective_n ──────────────────────────────────────────────────────────────


def test_effective_n_deduplicates():
    vp = _import_vp()
    s1 = MagicMock()
    s1.ticker = "AAPL"
    s1.created_at = datetime(2026, 3, 1)

    s2 = MagicMock()
    s2.ticker = "AAPL"
    s2.created_at = datetime(2026, 3, 1)  # Same day = same bet

    s3 = MagicMock()
    s3.ticker = "NVDA"
    s3.created_at = datetime(2026, 3, 1)

    assert vp._effective_n([s1, s2, s3]) == 2


def test_effective_n_different_days():
    vp = _import_vp()
    s1 = MagicMock()
    s1.ticker = "AAPL"
    s1.created_at = datetime(2026, 3, 1)

    s2 = MagicMock()
    s2.ticker = "AAPL"
    s2.created_at = datetime(2026, 3, 2)

    assert vp._effective_n([s1, s2]) == 2


def test_effective_n_empty():
    vp = _import_vp()
    assert vp._effective_n([]) == 0


# ── _fetch_prices ─────────────────────────────────────────────────────────────


def test_fetch_prices_empty():
    vp = _import_vp()
    assert vp._fetch_prices([]) == {}


def test_fetch_prices_yfinance_error():
    vp = _import_vp()
    with patch("yfinance.download", side_effect=Exception("network error")):
        result = vp._fetch_prices(["AAPL"])
    assert result == {}


def test_fetch_prices_returns_dict():
    vp = _import_vp()
    # Just verify it handles exceptions gracefully
    with patch("yfinance.download", side_effect=Exception("api error")):
        result = vp._fetch_prices(["AAPL", "NVDA"])
    assert result == {}
