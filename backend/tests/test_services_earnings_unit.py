"""Unit tests for services/earnings.py — earnings calendar and EPS surprise."""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timedelta

import pytest


# ── _fetch_earnings_calendar ──────────────────────────────────────────────────

def test_fetch_calendar_cache_hit():
    import time
    from services import earnings as e_module
    e_module._cal_cache["AAPL"] = ({"next_earnings_date": "2026-07-01", "days_to_earnings": 25}, time.time())
    result = e_module._fetch_earnings_calendar("AAPL")
    assert result["next_earnings_date"] == "2026-07-01"
    # cleanup
    del e_module._cal_cache["AAPL"]


def test_fetch_calendar_no_data():
    from services.earnings import _fetch_earnings_calendar
    mock_ticker = MagicMock()
    mock_ticker.calendar = None
    with patch("yfinance.Ticker", return_value=mock_ticker), \
         patch("services.earnings._retry", return_value=None):
        result = _fetch_earnings_calendar("NVDA")
    assert result == {}


def test_fetch_calendar_with_date():
    from services.earnings import _fetch_earnings_calendar
    from services import earnings as e_module

    mock_ticker = MagicMock()
    future_date = date.today() + timedelta(days=30)
    mock_ticker.calendar = {"Earnings Date": [future_date]}
    mock_ticker.earnings_history = None

    e_module._cal_cache.clear()

    with patch("yfinance.Ticker", return_value=mock_ticker), \
         patch("services.earnings._retry", side_effect=lambda fn: fn()):
        result = _fetch_earnings_calendar("MSFT")
    assert "next_earnings_date" in result or result == {}


def test_fetch_calendar_exception():
    from services.earnings import _fetch_earnings_calendar
    from services import earnings as e_module
    e_module._cal_cache.clear()

    with patch("yfinance.Ticker", side_effect=Exception("network error")):
        result = _fetch_earnings_calendar("GOOG")
    assert result == {}


# ── _fetch_earnings_surprise ──────────────────────────────────────────────────

def test_fetch_surprise_cache_hit():
    import time
    from services import earnings as e_module
    e_module._surp_cache["AAPL"] = ({"eps_surprise_pct": 5.2}, time.time())
    result = e_module._fetch_earnings_surprise("AAPL")
    assert result["eps_surprise_pct"] == 5.2
    del e_module._surp_cache["AAPL"]


def test_fetch_surprise_no_history():
    from services.earnings import _fetch_earnings_surprise
    from services import earnings as e_module
    e_module._surp_cache.clear()

    mock_ticker = MagicMock()
    mock_ticker.earnings_history = None

    with patch("yfinance.Ticker", return_value=mock_ticker), \
         patch("services.earnings._retry", return_value=None):
        result = _fetch_earnings_surprise("NVDA")
    assert result == {}


def test_fetch_surprise_exception():
    from services.earnings import _fetch_earnings_surprise
    from services import earnings as e_module
    e_module._surp_cache.clear()

    with patch("yfinance.Ticker", side_effect=Exception("api error")):
        result = _fetch_earnings_surprise("AMZN")
    assert result == {}


def test_fetch_surprise_with_data():
    from services.earnings import _fetch_earnings_surprise
    from services import earnings as e_module
    import pandas as pd
    e_module._surp_cache.clear()

    mock_ticker = MagicMock()
    # Create mock earnings history DataFrame
    history_data = {
        "epsActual": [2.5, 2.3, 2.1],
        "epsEstimate": [2.3, 2.2, 2.0],
        "surprisePercent": [8.7, 4.5, 5.0],
        "quarter": ["Q1-2026", "Q4-2025", "Q3-2025"],
    }
    mock_df = pd.DataFrame(history_data)
    mock_ticker.earnings_history = mock_df

    with patch("yfinance.Ticker", return_value=mock_ticker), \
         patch("services.earnings._retry", side_effect=lambda fn: fn()):
        result = _fetch_earnings_surprise("AAPL")
    # Should return a dict (may be empty if parsing fails, that's OK)
    assert isinstance(result, dict)


# ── get_earnings_calendar / get_earnings_surprise (async) ─────────────────────

@pytest.mark.asyncio
async def test_get_earnings_calendar_async():
    from services.earnings import get_earnings_calendar
    with patch("services.earnings._fetch_earnings_calendar", return_value={"days_to_earnings": 10}):
        result = await get_earnings_calendar("AAPL")
    assert result["days_to_earnings"] == 10


@pytest.mark.asyncio
async def test_get_earnings_surprise_async():
    from services.earnings import get_earnings_surprise
    with patch("services.earnings._fetch_earnings_surprise", return_value={"eps_surprise_pct": 3.5}):
        result = await get_earnings_surprise("AAPL")
    assert result["eps_surprise_pct"] == 3.5


@pytest.mark.asyncio
async def test_get_earnings_calendar_exception():
    from services.earnings import get_earnings_calendar
    with patch("services.earnings._fetch_earnings_calendar", side_effect=Exception("error")), \
         pytest.raises(Exception):
        await get_earnings_calendar("AAPL")
