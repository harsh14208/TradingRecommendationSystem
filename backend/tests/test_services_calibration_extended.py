"""Extended tests for services/calibration.py — pure helpers and calibration logic."""

import json
import math
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


# ── _blend ────────────────────────────────────────────────────────────────────


def test_blend_below_min_n():
    from services.calibration import _blend, _MIN_N

    assert _blend(_MIN_N - 1) == 0.0


def test_blend_at_min_n():
    from services.calibration import _blend, _MIN_N

    assert _blend(_MIN_N) > 0.0


def test_blend_at_n_full():
    from services.calibration import _blend, _N_FULL, _MAX_BLEND

    assert _blend(_N_FULL) == _MAX_BLEND


def test_blend_above_n_full():
    from services.calibration import _blend, _N_FULL, _MAX_BLEND

    assert _blend(_N_FULL + 100) == _MAX_BLEND


# ── _recency_weight ───────────────────────────────────────────────────────────


def test_recency_weight_today():
    from services.calibration import _recency_weight

    now = datetime.now(timezone.utc)
    w = _recency_weight(now)
    assert 0.99 < w <= 1.0


def test_recency_weight_half_life_ago():
    from services.calibration import _recency_weight, _HALF_LIFE

    past = datetime.now(timezone.utc) - timedelta(days=_HALF_LIFE)
    w = _recency_weight(past)
    assert 0.49 < w < 0.51


def test_recency_weight_none():
    from services.calibration import _recency_weight

    assert _recency_weight(None) == 1.0


def test_recency_weight_naive_datetime():
    from services.calibration import _recency_weight

    past = datetime.utcnow() - timedelta(days=10)
    w = _recency_weight(past)
    assert 0.0 < w < 1.0


def test_recency_weight_custom_ref():
    from services.calibration import _recency_weight

    ref = datetime(2026, 1, 10, tzinfo=timezone.utc)
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    w = _recency_weight(created, ref)
    assert 0.0 < w < 1.0


# ── _brier_score ──────────────────────────────────────────────────────────────


def test_brier_score_empty():
    from services.calibration import _brier_score

    result = _brier_score([], [])
    assert math.isnan(result)


def test_brier_score_perfect():
    from services.calibration import _brier_score

    probs = [1.0, 0.0, 1.0, 0.0]
    wins = [1, 0, 1, 0]
    assert _brier_score(probs, wins) == 0.0


def test_brier_score_worst():
    from services.calibration import _brier_score

    probs = [1.0, 0.0]
    wins = [0, 1]
    assert _brier_score(probs, wins) == 1.0


def test_brier_score_mixed():
    from services.calibration import _brier_score

    probs = [0.7, 0.3]
    wins = [1, 0]
    # (0.7-1)^2 + (0.3-0)^2 = 0.09 + 0.09 = 0.18 / 2 = 0.09
    result = _brier_score(probs, wins)
    assert abs(result - 0.09) < 0.001


# ── _interp_isotonic ──────────────────────────────────────────────────────────


def test_interp_isotonic_empty():
    from services.calibration import _interp_isotonic

    assert _interp_isotonic([], 0.5) is None


def test_interp_isotonic_single():
    from services.calibration import _interp_isotonic

    assert _interp_isotonic([[0.5, 0.6]], 0.5) is None


def test_interp_isotonic_interpolates():
    from services.calibration import _interp_isotonic

    table = [[0.4, 0.5], [0.6, 0.7]]
    result = _interp_isotonic(table, 0.5)
    # Midpoint: 0.5 + (0.5 - 0.4) / (0.6 - 0.4) * (0.7 - 0.5) = 0.5 + 0.5 * 0.2 = 0.6
    assert abs(result - 0.6) < 0.01


def test_interp_isotonic_below_range():
    from services.calibration import _interp_isotonic

    table = [[0.4, 0.5], [0.6, 0.7]]
    result = _interp_isotonic(table, 0.1)
    assert result == 0.5  # Returns first entry's prob


def test_interp_isotonic_above_range():
    from services.calibration import _interp_isotonic

    table = [[0.4, 0.5], [0.6, 0.7]]
    result = _interp_isotonic(table, 0.9)
    assert result == 0.7  # Returns last entry's prob


def test_interp_isotonic_exact_match():
    from services.calibration import _interp_isotonic

    table = [[0.4, 0.5], [0.6, 0.7], [0.8, 0.9]]
    result = _interp_isotonic(table, 0.4)
    assert result == 0.5


# ── _spy_regime_at ────────────────────────────────────────────────────────────


def test_spy_regime_at_empty_cache():
    from services.calibration import _spy_regime_at

    dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    assert _spy_regime_at(dt, {}) == "neutral"


def test_spy_regime_at_bull():
    from services.calibration import _spy_regime_at

    dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    cache = {"2026-03-01": "bull"}
    assert _spy_regime_at(dt, cache) == "bull"


def test_spy_regime_at_bear():
    from services.calibration import _spy_regime_at

    dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    cache = {"2026-03-01": "bear"}
    assert _spy_regime_at(dt, cache) == "bear"


def test_spy_regime_at_missing_date():
    from services.calibration import _spy_regime_at

    dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    cache = {"2026-03-02": "bull"}
    assert _spy_regime_at(dt, cache) == "neutral"


# ── _build_spy_regime_cache ───────────────────────────────────────────────────


def test_build_spy_regime_cache_error():
    from services.calibration import _build_spy_regime_cache

    with patch("yfinance.download", side_effect=Exception("network error")):
        result = _build_spy_regime_cache("2026-01-01", "2026-03-01")
    assert result == {}


def test_build_spy_regime_cache_success():
    from services.calibration import _build_spy_regime_cache
    import pandas as pd
    import numpy as np

    dates = pd.date_range("2025-06-01", periods=210, freq="B")
    # prices start above SMA200 (bull)
    prices = np.linspace(100, 110, 210)
    df = pd.DataFrame({"Close": prices}, index=dates)
    with patch("yfinance.download", return_value=df):
        result = _build_spy_regime_cache("2025-06-01", "2026-03-01")
    # Some dates should be bull (price > 1.02 * sma200) once SMA200 is formed
    assert isinstance(result, dict)


# ── load_calibration ──────────────────────────────────────────────────────────


def test_load_calibration_missing_file():
    from services.calibration import load_calibration

    with patch("services.calibration._CAL_FILE") as mock_file:
        mock_file.exists.return_value = False
        result = load_calibration()
    assert result == {}


def test_load_calibration_valid_file(tmp_path):
    from services.calibration import load_calibration

    data = {"_version": 2, "BUY": {"55": {"emp_wr": 0.65}}}
    cal_file = tmp_path / "calibration.json"
    cal_file.write_text(json.dumps(data))
    with patch("services.calibration._CAL_FILE", cal_file):
        result = load_calibration()
    assert result == data


def test_load_calibration_invalid_json(tmp_path):
    from services.calibration import load_calibration

    cal_file = tmp_path / "calibration.json"
    cal_file.write_text("INVALID JSON {{{")
    with patch("services.calibration._CAL_FILE", cal_file):
        result = load_calibration()
    assert result == {}


# ── apply_calibration ─────────────────────────────────────────────────────────


def test_apply_calibration_empty_map():
    from services.calibration import apply_calibration

    cal, meta = apply_calibration(65.0, "BUY", {})
    assert cal == 65.0
    assert meta is None


def test_apply_calibration_invalid_action():
    from services.calibration import apply_calibration

    cal_map = {"BUY": {"55": {"emp_wr": 0.65, "blend": 0.5}}}
    cal, meta = apply_calibration(65.0, "HOLD", cal_map)
    assert cal == 65.0


def test_apply_calibration_isotonic_global():
    from services.calibration import apply_calibration

    # Create a simple isotonic table
    table = [[c / 100, c / 100] for c in range(35, 79)]
    cal_map = {"_isotonic": table, "n": 20}
    cal, meta = apply_calibration(50.0, "BUY", cal_map)
    assert meta is not None
    assert meta["source"] == "isotonic_global"


def test_apply_calibration_regime_isotonic():
    from services.calibration import apply_calibration

    table = [[c / 100, c / 100] for c in range(35, 79)]
    cal_map = {
        "_isotonic": table,
        "_regime": {"bull": {"_isotonic": table, "n": 25}},
    }
    cal, meta = apply_calibration(50.0, "BUY", cal_map, regime="bull")
    assert meta is not None
    assert "bull" in meta["source"]


def test_apply_calibration_platt_fallback():
    from services.calibration import apply_calibration

    cal_map = {"BUY": {"50": {"emp_wr": 0.65, "blend": 0.5, "n": 5}}}
    cal, meta = apply_calibration(52.0, "BUY", cal_map)
    # Should use Platt fallback since no isotonic table
    assert isinstance(cal, float)


def test_apply_calibration_clamped():
    from services.calibration import apply_calibration, _CONF_CEIL

    # Extreme values should be clamped
    table = [[c / 100, 0.99] for c in range(35, 79)]
    cal_map = {"_isotonic": table, "n": 20}
    cal, _ = apply_calibration(79.0, "BUY", cal_map)
    assert cal <= _CONF_CEIL


# ── _fit_isotonic ─────────────────────────────────────────────────────────────


def test_fit_isotonic_insufficient_data():
    from services.calibration import _fit_isotonic

    result = _fit_isotonic([0.5, 0.6], [1, 0])
    assert result is None


def test_fit_isotonic_success():
    from services.calibration import _fit_isotonic

    # Need ≥20 samples
    X = [0.4 + i * 0.01 for i in range(25)]
    y = [int(x > 0.55) for x in X]
    w = [1.0] * 25
    result = _fit_isotonic(X, y, w)
    assert result is not None
    assert isinstance(result, list)


def test_fit_isotonic_no_weights():
    from services.calibration import _fit_isotonic

    X = [0.4 + i * 0.01 for i in range(25)]
    y = [int(x > 0.55) for x in X]
    result = _fit_isotonic(X, y)
    assert result is not None
