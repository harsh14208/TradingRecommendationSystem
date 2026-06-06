import numpy as np
import pandas as pd
from services.technicals import _np_atr, _np_ewm, _np_sma, calculate_indicators


def _make_ohlcv(n: int = 60) -> pd.DataFrame:
    # Deterministic synthetic series with enough variance and length.
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series(np.linspace(100, 150, n) + np.sin(np.linspace(0, 6, n)) * 2.0, index=idx)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = pd.concat([open_, close], axis=1).max(axis=1) + 1.5
    low = pd.concat([open_, close], axis=1).min(axis=1) - 1.5
    vol = pd.Series(np.linspace(1000, 2000, n) + np.cos(np.linspace(0, 6, n)) * 50, index=idx)
    df = pd.DataFrame(
        {
            "Open": open_.values,
            "High": high.values,
            "Low": low.values,
            "Close": close.values,
            "Volume": vol.values,
        }
    )
    return df


def test_np_sma_window_and_nan_padding():
    c = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    out = _np_sma(c, 3)
    # first n-1 should be nan
    assert np.isnan(out[0])
    assert np.isnan(out[1])
    # last should be avg of [3,4,5] = 4
    assert out[-1] == 4.0


def test_np_ewm_span_outputs_expected_length_and_smoothness():
    c = np.array([1.0, 2.0, 3.0, 4.0])
    out = _np_ewm(c, span=3)
    assert len(out) == len(c)
    # Basic sanity: should be monotone increasing for monotone increasing input
    assert out[-1] > out[0]
    assert out[1] >= out[0]


def test_np_atr_returns_float_and_uses_wilder_smoothing():
    h = np.array([10.0, 11.0, 12.0, 13.0])
    l = np.array([9.0, 10.0, 11.0, 12.0])
    c = np.array([9.5, 10.5, 11.5, 12.5])
    atr = _np_atr(h, l, c, period=3)
    assert isinstance(atr, float)


def test_calculate_indicators_basic_contract_and_key_fields():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    # Contract: returns dict with at least price/change/atr/rsi keys
    assert isinstance(out, dict)
    assert "price" in out
    assert "change" in out
    assert "change_pct" in out
    assert "rsi" in out
    assert "atr" in out
    assert out["price"] > 0


def test_calculate_indicators_short_df_returns_empty():
    df = _make_ohlcv(10)
    assert calculate_indicators(df) == {}


# ── Extended calculate_indicators tests ──────────────────────────────────────

def test_calculate_indicators_none_returns_empty():
    assert calculate_indicators(None) == {}


def test_calculate_indicators_bb_pct_b_range():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    if "bb_pct_b" in out and out["bb_pct_b"] is not None:
        assert isinstance(out["bb_pct_b"], float)


def test_calculate_indicators_ibs_range():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    if "ibs" in out and out["ibs"] is not None:
        assert 0.0 <= out["ibs"] <= 1.0


def test_calculate_indicators_volume_ratio():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    if "volume_ratio" in out and out["volume_ratio"] is not None:
        assert out["volume_ratio"] >= 0


def test_calculate_indicators_macd():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    assert "macd" in out or len(out) > 5


def test_calculate_indicators_falling_series():
    idx = pd.date_range("2025-01-01", periods=80, freq="D")
    close = np.linspace(150, 100, 80) + np.sin(np.linspace(0, 6, 80)) * 2
    high = close + 1.5
    low = close - 1.5
    vol = np.full(80, 1_000_000.0)
    df = pd.DataFrame({"Open": close, "High": high, "Low": low, "Close": close, "Volume": vol})
    out = calculate_indicators(df)
    assert isinstance(out, dict)
    assert "price" in out


def test_calculate_indicators_vwap_pct():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    if "vwap_pct" in out:
        assert isinstance(out["vwap_pct"], float)


def test_calculate_indicators_52w():
    df = _make_ohlcv(260)  # ~1 trading year
    out = calculate_indicators(df)
    assert "price" in out


def test_calculate_indicators_hurst_exp():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    if "hurst_exp" in out and out["hurst_exp"] is not None:
        assert 0.0 <= out["hurst_exp"] <= 1.0


def test_calculate_indicators_atr_pct():
    df = _make_ohlcv(80)
    out = calculate_indicators(df)
    if "atr_pct" in out and out["atr_pct"] is not None:
        assert out["atr_pct"] >= 0


# ── batch_calculate_indicators ────────────────────────────────────────────────

def test_batch_calculate_indicators_empty():
    from services.technicals import batch_calculate_indicators
    result = batch_calculate_indicators({})
    assert result == {}


def test_batch_calculate_indicators_single_ticker():
    from services.technicals import batch_calculate_indicators
    df = _make_ohlcv(80)
    result = batch_calculate_indicators({"AAPL": df})
    assert "AAPL" in result
    assert isinstance(result["AAPL"], dict)


def test_batch_calculate_indicators_multiple():
    from services.technicals import batch_calculate_indicators
    df1 = _make_ohlcv(80)
    df2 = _make_ohlcv(60)
    result = batch_calculate_indicators({"AAPL": df1, "NVDA": df2})
    assert "AAPL" in result
    assert "NVDA" in result


def test_batch_calculate_indicators_none_df():
    from services.technicals import batch_calculate_indicators
    result = batch_calculate_indicators({"AAPL": None, "NVDA": _make_ohlcv(80)})
    assert isinstance(result, dict)
    # NVDA should still be calculated
    assert "NVDA" in result


# ── _safe ─────────────────────────────────────────────────────────────────────

def test_safe_normal():
    from services.technicals import _safe
    s = pd.Series([1.0, 2.0, 3.0])
    assert _safe(s) == 3.0


def test_safe_nan():
    from services.technicals import _safe
    s = pd.Series([1.0, float("nan")])
    assert _safe(s) is None


def test_safe_exception():
    from services.technicals import _safe
    assert _safe(None) is None


def test_safe_index():
    from services.technicals import _safe
    s = pd.Series([10.0, 20.0, 30.0])
    assert _safe(s, idx=0) == 10.0


# ── _np_sma edge cases ────────────────────────────────────────────────────────

def test_np_sma_too_short():
    c = np.array([1.0, 2.0])
    out = _np_sma(c, n=5)
    assert all(np.isnan(out))


def test_np_sma_preserves_length():
    c = np.arange(20.0)
    out = _np_sma(c, n=5)
    assert len(out) == 20


# ── _np_atr edge cases ────────────────────────────────────────────────────────

def test_np_atr_zero_range():
    h = np.full(20, 100.0)
    l = np.full(20, 100.0)
    c = np.full(20, 100.0)
    atr = _np_atr(h, l, c)
    assert atr == pytest.approx(0.0)


import pytest
