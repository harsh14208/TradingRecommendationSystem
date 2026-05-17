import pytest
from unittest.mock import patch, AsyncMock
from services.massive_economy import get_economy_data

@pytest.mark.asyncio
async def test_get_economy_data_success():
    async def mock_fetch(session, endpoint, params):
        if "treasury" in endpoint:
            return [{"yield_2y": 4.5, "yield_10y": 4.1, "yield_30y": 4.2}]
        if "inflation" in endpoint:
            return [{"cpi_yoy": 3.1, "pce_yoy": 2.8}]
        if "labor" in endpoint:
            return [{"unemployment_rate": 3.9, "nonfarm_payrolls": 250000}]
        return []

    with patch("services.massive_economy.os.getenv", return_value="TEST_KEY"), \
         patch("services.massive_economy._fetch", side_effect=mock_fetch):
        
        # Clear cache to force fetch
        from services.massive_economy import _cache
        _cache["data"] = None
        
        data = await get_economy_data()
        
        assert data["yield_10y"] == 4.1
        assert data["cpi_yoy"] == 3.1
        assert data["unemployment"] == 3.9
        assert data["nfp_change_k"] == 250.0

@pytest.mark.asyncio
async def test_get_economy_data_no_key():
    with patch("services.massive_economy.os.getenv", return_value=None):
        # Clear cache
        from services.massive_economy import _cache
        _cache["data"] = None
        
        data = await get_economy_data()
        assert data == {}