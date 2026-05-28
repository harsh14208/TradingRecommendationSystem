from unittest.mock import AsyncMock, patch

import pytest
from services.massive_options import get_option_chain_signals, score_option_chain


@pytest.mark.asyncio
async def test_get_option_chain_signals_success():
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.json.return_value = {
        "results": [
            # ATM options
            {
                "strike_price": 100,
                "contract_type": "call",
                "open_interest": 1000,
                "greeks": {"gamma": 0.05, "delta": 0.5},
                "implied_volatility": 0.3,
            },
            {
                "strike_price": 100,
                "contract_type": "put",
                "open_interest": 500,
                "greeks": {"gamma": 0.05, "delta": -0.5},
                "implied_volatility": 0.35,
            },
            # 25-delta options for skew
            {
                "strike_price": 110,
                "contract_type": "call",
                "open_interest": 100,
                "greeks": {"gamma": 0.01, "delta": 0.25},
                "implied_volatility": 0.25,
            },
            {
                "strike_price": 90,
                "contract_type": "put",
                "open_interest": 100,
                "greeks": {"gamma": 0.01, "delta": -0.25},
                "implied_volatility": 0.35,
            },
        ]
    }

    with (
        patch("services.massive_options.os.getenv", return_value="TEST_KEY"),
        patch("services.massive_options.aiohttp.ClientSession.get") as m_get,
    ):
        m_get.return_value.__aenter__.return_value = mock_resp

        # Clear cache
        from services.massive_options import _cache

        _cache.clear()

        res = await get_option_chain_signals("AAPL", 100.0)

        assert res is not None
        assert res["contracts_parsed"] == 4
        assert "net_gex" in res
        # d25_put_iv (0.35) - d25_call_iv (0.25) -> skew = 10.0
        assert res["skew_25d"] == 10.0
        assert res["atm_call_iv"] == 30.0


@pytest.mark.asyncio
async def test_get_option_chain_signals_no_key():
    with patch("services.massive_options.os.getenv", return_value=None):
        from services.massive_options import _cache

        _cache.clear()

        res = await get_option_chain_signals("AAPL", 100.0)
        assert res == {}


def test_score_option_chain():
    # Test High GEX (Dealer long gamma)
    score1, rat1 = score_option_chain({"net_gex": 3.0, "max_pain": 100}, 100.0, "BUY")
    assert score1 == -3.0
    assert any("Dealer Long Gamma" in r["head"] for r in rat1)

    # Test Low GEX (Dealer short gamma)
    score2, rat2 = score_option_chain({"net_gex": -3.0, "max_pain": 100}, 100.0, "BUY")
    assert score2 == 3.0

    # Test high put skew (Fear indicator)
    score3, rat3 = score_option_chain({"skew_25d": 10.0}, 100.0, "BUY")
    assert score3 == 4.0

    # Test max pain gravitational pull (Gap > 3%)
    score4, rat4 = score_option_chain({"max_pain": 105.0}, 100.0, "BUY")
    # Gap is 5% upward pull
    assert any("Gravitational Pull" in r["head"] for r in rat4)
    assert any("Upward" in r["head"] for r in rat4)
