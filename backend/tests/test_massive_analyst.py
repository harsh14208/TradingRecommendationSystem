from unittest.mock import patch

import pytest
from services.massive_analyst import get_analyst_intelligence


@pytest.mark.asyncio
async def test_get_analyst_intelligence_success():
    async def mock_fetch(session, endpoint, params):
        if "bulls_bears" in endpoint:
            return {"bull_count": 6, "bear_count": 2, "bull_summary": "Strong momentum", "bear_summary": "Overvalued"}
        if "consensus" in endpoint:
            return {"consensus": "strong_buy", "target_price_average": 150.0, "analyst_count": 10}
        return {}

    async def mock_fetch_list(session, endpoint, params):
        if "guidance" in endpoint:
            return [{"eps_direction": "raise", "eps_estimate": "1.50"}]
        return []

    with (
        patch("services.massive_analyst.os.getenv", return_value="TEST_KEY"),
        patch("services.massive_analyst._fetch", side_effect=mock_fetch),
        patch("services.massive_analyst._fetch_list", side_effect=mock_fetch_list),
    ):
        from services.massive_analyst import _cache

        _cache.clear()

        res = await get_analyst_intelligence("AAPL")

        assert res is not None
        # Math: 3.0 + (ratio 3 - 1)*0.5 = 4.0
        assert res["bulls_bears"]["score"] == 4.0
        assert res["bulls_bears"]["label"] == "bullish"

        # Math: strong_buy maps to 6
        assert res["consensus"]["score"] == 6.0
        assert res["consensus"]["key"] == "strong_buy"

        # Math: eps raise maps to 8.0
        assert res["guidance"]["score"] == 8.0

        # Sum of components
        assert res["total_score"] == 18.0


@pytest.mark.asyncio
async def test_get_analyst_intelligence_no_key():
    with patch("services.massive_analyst.os.getenv", return_value=None):
        from services.massive_analyst import _cache

        _cache.clear()

        res = await get_analyst_intelligence("AAPL")
        assert res == {}
