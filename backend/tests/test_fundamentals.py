import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import pandas as pd

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.fundamentals import get_fundamentals, _fund_cache


@pytest.fixture(autouse=True)
def clear_cache():
    _fund_cache.clear()
    yield
    _fund_cache.clear()

@pytest.mark.asyncio
async def test_get_fundamentals_success():
    mock_info = {
        "marketCap": 1000000,
        "dividendYield": 0.05,
        "sharesOutstanding": 100000000
    }
    
    mock_bs = pd.DataFrame({
        "2023": [500000, 200000, 300000, 100000],
        "2022": [400000, 150000, 250000, 95000]
    }, index=["Total Assets", "Total Liabilities", "Stockholders Equity", "Long Term Debt"])
    
    mock_fin = pd.DataFrame({
        "2023": [1000000, 600000, 100000],
        "2022": [900000, 550000, 80000]
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])

    mock_cf = pd.DataFrame({
        "2023": [150000, -50000, -20000],
        "2022": [120000, -40000, -10000]
    }, index=["Operating Cash Flow", "Capital Expenditures", "Repurchase Of Capital Stock"])
    
    mock_ticker_inst = MagicMock()
    mock_ticker_inst.info = mock_info
    mock_ticker_inst.balance_sheet = mock_bs
    mock_ticker_inst.financials = mock_fin
    mock_ticker_inst.cashflow = mock_cf
    mock_ticker_inst.quarterly_financials = pd.DataFrame()
    mock_ticker_inst.quarterly_balance_sheet = pd.DataFrame()
    mock_ticker_inst.quarterly_cashflow = pd.DataFrame()

    with patch("services.fundamentals.yf.Ticker", return_value=mock_ticker_inst):
        res = await get_fundamentals("AAPL")
        
        assert "piotroski_f" in res
        assert res.get("fcf") == 100000  # 150k - 50k
        assert res.get("fcf_yield") == 10.0 # 100k / 1M * 100
        assert res.get("buyback_yield") == 2.0 # 20k / 1M * 100
        assert res.get("div_yield_pct") == 5.0

@pytest.mark.asyncio
async def test_get_fundamentals_exception_handled():
    with patch("services.fundamentals.yf.Ticker", side_effect=Exception("API Error")):
        res = await get_fundamentals("INVALID")
        assert res == {}

@pytest.mark.asyncio
async def test_get_fundamentals_missing_data():
    # Simulating empty responses from yfinance for a newly listed or opaque stock
    mock_ticker_inst = MagicMock()
    mock_ticker_inst.info = {}
    mock_ticker_inst.balance_sheet = pd.DataFrame()
    mock_ticker_inst.financials = pd.DataFrame()
    mock_ticker_inst.cashflow = pd.DataFrame()
    mock_ticker_inst.quarterly_financials = pd.DataFrame()
    mock_ticker_inst.quarterly_balance_sheet = pd.DataFrame()
    mock_ticker_inst.quarterly_cashflow = pd.DataFrame()

    with patch("services.fundamentals.yf.Ticker", return_value=mock_ticker_inst):
        res = await get_fundamentals("NEWSTOCK")
        assert "piotroski_f" in res
        assert res["piotroski_f"] == 0 # no data means 0 score
        assert "fcf_yield" not in res

@pytest.mark.asyncio
async def test_get_fundamentals_caching():
    mock_ticker_inst = MagicMock()
    mock_ticker_inst.info = {"marketCap": 2000000}
    mock_ticker_inst.balance_sheet = pd.DataFrame()
    mock_ticker_inst.financials = pd.DataFrame()
    mock_ticker_inst.cashflow = pd.DataFrame()
    mock_ticker_inst.quarterly_financials = pd.DataFrame()
    mock_ticker_inst.quarterly_balance_sheet = pd.DataFrame()
    mock_ticker_inst.quarterly_cashflow = pd.DataFrame()

    with patch("services.fundamentals.yf.Ticker", return_value=mock_ticker_inst) as m_ticker:
        _fund_cache.clear()
        
        # First call fetches data
        res1 = await get_fundamentals("MSFT")
        assert m_ticker.call_count == 1
        
        # Second call returns cached data
        res2 = await get_fundamentals("MSFT")
        assert m_ticker.call_count == 1
        assert res1 == res2