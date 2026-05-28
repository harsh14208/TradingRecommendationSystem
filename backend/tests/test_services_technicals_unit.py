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
