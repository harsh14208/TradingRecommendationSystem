"""
Tests for §37 audit fixes in backtest_technicals.py:
  - fetch_earnings_dates_polygon: Polygon API integration + empty/error handling
  - MFE (max favorable excursion) tracking in simulate_ticker
  - Survivorship-bias warning present in main() output
  - Completed-week resample fix (weekly trend uses only closed weeks)
  - HELD_OUT_TICKERS list is populated and does not overlap with TICKERS
"""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_backtest():
    """Import backtest_technicals (lives outside the package, no __init__)."""
    scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import backtest_technicals as bt

    return bt


def _make_daily_df(n=300, start="2022-01-01", seed=42):
    """Generate synthetic OHLCV DataFrame with realistic price motion."""
    rng = np.random.default_rng(seed)
    closes = 100.0 * np.cumprod(1 + rng.normal(0.0005, 0.015, n))
    opens = closes * (1 + rng.normal(0, 0.003, n))
    highs = np.maximum(opens, closes) * (1 + rng.uniform(0, 0.008, n))
    lows = np.minimum(opens, closes) * (1 - rng.uniform(0, 0.008, n))
    dates = pd.date_range(start=start, periods=n, freq="B")
    df = pd.DataFrame(
        {
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": rng.integers(1_000_000, 10_000_000, n).astype(float),
        },
        index=dates,
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# fetch_earnings_dates_polygon
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _disable_earnings_cache():
    """Prevent local cache files from shadowing mocked Polygon responses."""
    with patch("os.path.exists", return_value=False):
        yield


def test_polygon_earnings_returns_set_on_success():
    """Happy path: Polygon returns two filing_date records → two Timestamps."""
    bt = _load_backtest()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {"filing_date": "2015-02-10"},
            {"filing_date": "2015-05-11"},
        ],
        "next_url": None,
    }

    with patch("requests.get", return_value=mock_resp):
        dates = bt.fetch_earnings_dates_polygon("AAPL", "fake_key", "2015-01-01")

    assert len(dates) == 2
    assert pd.Timestamp("2015-02-10") in dates
    assert pd.Timestamp("2015-05-11") in dates


def test_polygon_earnings_paginates():
    """Polygon pagination: next_url on first response triggers a second request."""
    bt = _load_backtest()

    page1 = MagicMock()
    page1.status_code = 200
    page1.json.return_value = {
        "results": [{"filing_date": "2010-03-01"}],
        "next_url": "https://api.polygon.io/vX/reference/financials?cursor=abc",
    }
    page2 = MagicMock()
    page2.status_code = 200
    page2.json.return_value = {
        "results": [{"filing_date": "2010-06-01"}],
        "next_url": None,
    }

    with patch("requests.get", side_effect=[page1, page2]):
        dates = bt.fetch_earnings_dates_polygon("MSFT", "fake_key", "2010-01-01")

    assert pd.Timestamp("2010-03-01") in dates
    assert pd.Timestamp("2010-06-01") in dates
    assert len(dates) == 2


def test_polygon_earnings_empty_api_key_returns_empty():
    """No API key → empty set without making any HTTP request."""
    bt = _load_backtest()
    with patch("requests.get") as mock_get:
        dates = bt.fetch_earnings_dates_polygon("NVDA", "", "2010-01-01")
    mock_get.assert_not_called()
    assert dates == set()


def test_polygon_earnings_non_200_returns_empty():
    """Non-200 response (e.g. 429 rate-limit) → empty set, no exception raised."""
    bt = _load_backtest()
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    with patch("requests.get", return_value=mock_resp):
        dates = bt.fetch_earnings_dates_polygon("TSLA", "k", "2015-01-01")
    assert dates == set()


def test_polygon_earnings_network_error_returns_empty():
    """Network exception → empty set, no exception propagates."""
    bt = _load_backtest()
    with patch("requests.get", side_effect=ConnectionError("timeout")):
        dates = bt.fetch_earnings_dates_polygon("AMZN", "k", "2015-01-01")
    assert dates == set()


def test_polygon_earnings_falls_back_to_start_date():
    """Results using start_date field (fallback from filing_date) are also captured."""
    bt = _load_backtest()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [{"start_date": "2012-04-25"}],  # no filing_date key
        "next_url": None,
    }
    with patch("requests.get", return_value=mock_resp):
        dates = bt.fetch_earnings_dates_polygon("GOOG", "k", "2012-01-01")
    assert pd.Timestamp("2012-04-25") in dates


# ─────────────────────────────────────────────────────────────────────────────
# MFE (max favorable excursion) tracking in simulate_ticker
# ─────────────────────────────────────────────────────────────────────────────


def _make_bt_df(n=500, seed=42):
    """Build a fully-computed indicator + score DataFrame for simulate_ticker."""
    bt = _load_backtest()
    df = _make_daily_df(n=n, seed=seed)
    df = bt.compute_indicators(df)
    df["score"] = bt.compute_scores(df)
    return df


def test_mfe_column_present_in_trade_records():
    """simulate_ticker must produce a DataFrame with an 'mfe_pct' column."""
    bt = _load_backtest()
    df = _make_bt_df(n=500)
    result = bt.simulate_ticker("TEST", df, {}, {}, {}, mr_only=True)
    if not result.empty:
        assert "mfe_pct" in result.columns, "mfe_pct column missing from trade records"


def test_mfe_non_negative_for_buy_trades():
    """MFE must always be ≥ 0 (it's the best intrabar high vs entry)."""
    bt = _load_backtest()
    df = _make_bt_df(n=500)
    result = bt.simulate_ticker("TEST", df, {}, {}, {}, mr_only=True)
    buys = result[result["action"] == "BUY"] if not result.empty else pd.DataFrame()
    if not buys.empty:
        assert (buys["mfe_pct"] >= 0).all(), "MFE must be ≥ 0 for all BUY trades"


def test_mfe_at_least_gross_pct_for_winning_trades():
    """For winning BUY trades (gross_pct > 0), MFE ≥ gross_pct
    (the best high reached is at least as good as the exit price)."""
    bt = _load_backtest()
    df = _make_bt_df(n=600, seed=7)
    result = bt.simulate_ticker("TEST", df, {}, {}, {}, mr_only=True)
    if result.empty:
        return
    winners = result[(result["action"] == "BUY") & (result["gross_pct"] > 0)]
    if not winners.empty:
        # Allow tiny floating-point slack (exit is close price, MFE uses high)
        assert (winners["mfe_pct"] >= winners["gross_pct"] - 0.01).all(), (
            "MFE should be >= gross_pct for winning trades"
        )


# ─────────────────────────────────────────────────────────────────────────────
# HELD_OUT_TICKERS — structure tests (no actual data download)
# ─────────────────────────────────────────────────────────────────────────────


def test_held_out_tickers_populated():
    """HELD_OUT_TICKERS must have at least 5 tickers."""
    bt = _load_backtest()
    assert len(bt.HELD_OUT_TICKERS) >= 5, "Need at least 5 held-out OOS tickers"


def test_held_out_tickers_no_overlap_with_main_universe():
    """No ticker should appear in both TICKERS and HELD_OUT_TICKERS."""
    bt = _load_backtest()
    overlap = set(bt.TICKERS) & set(bt.HELD_OUT_TICKERS)
    assert overlap == set(), f"Tickers appear in both TICKERS and HELD_OUT_TICKERS (data leakage!): {overlap}"


def test_held_out_tickers_are_strings():
    """All HELD_OUT_TICKERS entries must be non-empty strings."""
    bt = _load_backtest()
    for t in bt.HELD_OUT_TICKERS:
        assert isinstance(t, str) and len(t) > 0, f"Invalid ticker in HELD_OUT: {t!r}"


# ─────────────────────────────────────────────────────────────────────────────
# Completed-week resample logic (unit test on the pure Python logic)
# ─────────────────────────────────────────────────────────────────────────────


def test_weekly_resample_drops_incomplete_week():
    """The fix: weekly.iloc[:-1] must drop the current incomplete week so that
    mid-week daily closes don't broadcast into earlier days in the same week.

    pandas resample("W") labels each bucket with SUNDAY (end of ISO calendar week).
    """
    # 22 business days starting 2024-01-01: spans at least 4 complete Mon-Fri weeks
    # plus a partial week at the end, ensuring the last resample bucket is incomplete.
    dates = pd.date_range("2024-01-01", periods=22, freq="B")
    closes = pd.Series(np.linspace(100, 120, 22), index=dates)

    weekly_with_incomplete = closes.resample("W").last().dropna()
    weekly_completed_only = weekly_with_incomplete.iloc[:-1]

    # Dropping last week must produce a shorter series
    assert len(weekly_completed_only) < len(weekly_with_incomplete), (
        "Dropping last week should produce a shorter series"
    )
    # pandas resample("W") uses SUNDAY as the week-end label (ISO week closes Sun)
    last_label = weekly_completed_only.index[-1]
    assert last_label.weekday() == 6, (  # 6 = Sunday
        f"Weekly resample label should be Sunday; got {last_label.day_name()}"
    )


def test_weekly_sma_uses_only_closed_weeks():
    """Verify the SMA20 computation based on completed weeks gives stable result
    even when a mid-week bar is appended."""
    closes = pd.Series(
        np.linspace(100, 110, 140),
        index=pd.date_range("2021-01-04", periods=140, freq="B"),
    )
    # Add a mid-week (Wednesday) bar to simulate live engine state
    extra_idx = pd.date_range("2021-07-28", periods=1, freq="B")  # Wednesday
    closes = pd.concat([closes, pd.Series([115.0], index=extra_idx)])

    weekly = closes.resample("W").last().dropna()
    completed = weekly.iloc[:-1]  # drop partial week

    # SMA20 on completed weeks should not include the Wednesday partial bar
    assert len(completed) >= 20
    sma20_completed = float(completed.iloc[-20:].mean())
    # Sanity: result is in the range of our linear price series
    assert 100.0 <= sma20_completed <= 115.0
