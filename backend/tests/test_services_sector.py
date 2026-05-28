from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
from services.sector import get_sector_relative_strength


@pytest.mark.asyncio
async def test_get_sector_relative_strength():
    # Create DataFrames with at least 21 records to satisfy the default lookback requirement
    mock_df = pd.DataFrame({"Close": [100.0 + i for i in range(25)]})
    mock_etf_df = pd.DataFrame({"Close": [100.0 + i * 0.5 for i in range(25)]})

    with patch("services.sector.get_history", new_callable=AsyncMock) as m_hist:
        m_hist.return_value = mock_etf_df

        res = await get_sector_relative_strength("AAPL", mock_df)
        assert res is not None
        assert "rs_vs_sector" in res


@pytest.mark.asyncio
async def test_get_sector_relative_strength_unmapped_ticker():
    # Ticker not in SECTOR_MAP
    res = await get_sector_relative_strength("UNKNOWN_TICKER")
    assert res is None


@pytest.mark.asyncio
async def test_get_sector_relative_strength_insufficient_data():
    # Create DataFrames with less than the 21 record lookback
    mock_df = pd.DataFrame({"Close": [100.0, 105.0]})
    mock_etf_df = pd.DataFrame({"Close": [100.0, 102.0]})

    with patch("services.sector.get_history", new_callable=AsyncMock) as m_hist:
        m_hist.return_value = mock_etf_df
        res = await get_sector_relative_strength("AAPL", mock_df, lookback=21)
        assert res is None


@pytest.mark.asyncio
async def test_get_sector_relative_strength_caching_and_fetch():
    mock_df = pd.DataFrame({"Close": [100.0 + i for i in range(25)]})
    mock_etf_df = pd.DataFrame({"Close": [100.0 + i * 0.5 for i in range(25)]})

    with patch("services.sector.get_history", new_callable=AsyncMock) as m_hist:
        from services.sector import _etf_cache

        _etf_cache.clear()

        # Setup return values: 1st fetch = ETF, 2nd fetch = Ticker
        m_hist.side_effect = [mock_etf_df, mock_df]

        # Call 1: Fetches ETF (and Ticker, because ticker_df isn't passed)
        await get_sector_relative_strength("MSFT")
        assert m_hist.call_count == 2

        # Call 2: Uses ETF Cache for "AAPL" (XLK). Passed ticker_df explicitly to skip ticker fetch
        await get_sector_relative_strength("AAPL", ticker_df=mock_df)
        assert m_hist.call_count == 2  # call count shouldn't increase


@pytest.mark.asyncio
async def test_get_sector_relative_strength_exception():
    with patch("services.sector.get_history", new_callable=AsyncMock) as m_hist:
        from services.sector import _etf_cache

        _etf_cache.clear()

        m_hist.side_effect = Exception("API error")
        res = await get_sector_relative_strength("AAPL")
        assert res is None
