import pytest
from unittest.mock import patch, AsyncMock
from services.fear_greed import get_fear_greed

@pytest.mark.asyncio
async def test_get_fear_greed_success():
    with patch("services.fear_greed._cache", {"data": None, "ts": 0}), \
         patch("services.fear_greed.cache_get", new_callable=AsyncMock) as m_cache_get, \
         patch("services.fear_greed.cache_set", new_callable=AsyncMock), \
         patch("services.fear_greed.aiohttp.ClientSession.get") as m_get:
        
        m_cache_get.return_value = None
        
        # Mock aiohttp response for CNN JSON structure
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json.return_value = {"fear_and_greed": {"score": 40.0, "previous_close": 46.0, "previous_1_week": 40.0, "previous_1_month": 50.0}}
        m_get.return_value.__aenter__.return_value = mock_resp
        
        res = await get_fear_greed()
        
        assert res is not None
        assert res.get("score") == 40.0
        # Should map the correct label based on the 40.0 value
        assert res.get("label") == "Fear"

@pytest.mark.asyncio
async def test_get_fear_greed_exception():
    with patch("services.fear_greed._cache", {"data": None, "ts": 0}), \
         patch("services.fear_greed.cache_get", new_callable=AsyncMock) as m_cache_get, \
         patch("services.fear_greed.cache_set", new_callable=AsyncMock), \
         patch("services.fear_greed.aiohttp.ClientSession.get") as m_get:
        
        m_cache_get.return_value = None
        m_get.side_effect = Exception("API error")
        
        res = await get_fear_greed()
        
        # System should fallback to neutral 50.0 gracefully on failures
        assert res is not None
        assert res.get("score") == 50.0
        assert res.get("label") == "Neutral"