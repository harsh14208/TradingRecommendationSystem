from unittest.mock import AsyncMock, MagicMock, patch

import pytest
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

    with (
        patch("services.massive_economy.os.getenv", return_value="TEST_KEY"),
        patch("services.massive_economy._fetch", side_effect=mock_fetch),
    ):
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


@pytest.mark.asyncio
async def test_get_economy_data_uses_cache():
    from services.massive_economy import _cache
    import time

    _cache["data"] = {"yield_10y": 4.0}
    _cache["ts"] = time.time()  # fresh

    data = await get_economy_data()
    assert data == {"yield_10y": 4.0}


@pytest.mark.asyncio
async def test_fetch_returns_results_on_200():
    from services.massive_economy import _fetch

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"results": [{"yield_10y": 4.0}]})

    resp_ctx = AsyncMock()
    resp_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    resp_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=resp_ctx)

    result = await _fetch(mock_session, "economy/treasury_yields", {"apiKey": "K"})
    assert result == [{"yield_10y": 4.0}]


@pytest.mark.asyncio
async def test_fetch_returns_empty_on_non_200():
    from services.massive_economy import _fetch

    mock_resp = AsyncMock()
    mock_resp.status = 403

    resp_ctx = AsyncMock()
    resp_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    resp_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=resp_ctx)

    result = await _fetch(mock_session, "economy/treasury_yields", {"apiKey": "K"})
    assert result == []


@pytest.mark.asyncio
async def test_fetch_returns_empty_on_exception():
    from services.massive_economy import _fetch

    mock_session = MagicMock()
    mock_session.get = MagicMock(side_effect=Exception("timeout"))

    result = await _fetch(mock_session, "economy/treasury_yields", {"apiKey": "K"})
    assert result == []
