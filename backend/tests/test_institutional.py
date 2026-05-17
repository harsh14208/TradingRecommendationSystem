import pytest
from unittest.mock import patch
from services.institutional import get_institutional_signals, _cusip_to_ticker

def test_cusip_to_ticker():
    # Valid case
    assert _cusip_to_ticker("037833100") == "AAPL"
    assert _cusip_to_ticker("594918104") == "MSFT"
    
    # Invalid case
    assert _cusip_to_ticker("INVALID12") is None

@pytest.mark.asyncio
async def test_get_institutional_signals_buy():
    async def mock_fetch_holdings(session, cik):
        return [
            {
                "ticker": "AAPL",
                "value_k": 5000,
                "shares": 10000,
                "action": "increased",
                "filing_date": "2026-05-10",
                "qoq_trend": "rising"
            }
        ]

    with patch("services.institutional._fetch_latest_13f_holdings", side_effect=mock_fetch_holdings):
        signals = await get_institutional_signals(["AAPL"])
        
        assert len(signals) == 1
        assert signals[0]["ticker"] == "AAPL"
        # It aggregates the rationale and tracks it as a BUY
        assert signals[0]["score"] > 0
        assert "Institutional buying" in signals[0]["rationale"]["head"]
        assert signals[0]["qoq_trend"] == "rising"