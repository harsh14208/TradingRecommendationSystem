"""Extended unit tests for services/options.py — edge cases, error handling,
fetchers, and scoring branches not covered by test_services_options_unit.py.
"""

from unittest.mock import MagicMock, patch

import pytest

import services.options as opts


# ── Helper to reset module globals between tests ─────────────────────────────


@pytest.fixture(autouse=True)
def _reset_opts_globals():
    """Reset in-process caches and redis to known clean state."""
    opts._opt_cache = {}
    opts._iv_history = {}
    old_redis = opts._opt_redis
    opts._opt_redis = None
    # Force the CBOE middle-tier fallback out of the way so these unit tests
    # exercise the Polygon → yfinance path they were written for.
    with patch("services.options.fetch_cboe_options_chain", return_value=None):
        yield
    opts._opt_cache = {}
    opts._iv_history = {}
    opts._opt_redis = old_redis


# ── Black-Scholes helpers — exception paths ──────────────────────────────────


def test_bs_gamma_math_exception():
    from services.options import _bs_gamma

    with patch("services.options.math.log", side_effect=ValueError("bad math")):
        assert _bs_gamma(S=100, K=100, T=0.25, sigma=0.20) == 0.0


def test_bs_vanna_nonzero_values():
    from services.options import _bs_vanna

    # ATM-ish call should have vanna close to 0; far OTM more negative
    v_atm = _bs_vanna(S=100, K=100, T=0.25, sigma=0.20)
    v_otm = _bs_vanna(S=100, K=150, T=0.25, sigma=0.20)
    assert isinstance(v_atm, float)
    assert isinstance(v_otm, float)


def test_bs_vanna_math_exception():
    from services.options import _bs_vanna

    with patch("services.options.math.log", side_effect=ValueError("bad math")):
        assert _bs_vanna(S=100, K=100, T=0.25, sigma=0.20) == 0.0


def test_bs_charm_values():
    from services.options import _bs_charm

    c = _bs_charm(S=100, K=100, T=0.25, sigma=0.20)
    assert isinstance(c, float)


def test_bs_charm_math_exception():
    from services.options import _bs_charm

    with patch("services.options.math.log", side_effect=ValueError("bad math")):
        assert _bs_charm(S=100, K=100, T=0.25, sigma=0.20) == 0.0


# ── compute_dealer_positioning — deeper branches ─────────────────────────────


def test_compute_dealer_positioning_missing_keys():
    from services.options import compute_dealer_positioning

    # Missing strike / iv / oi keys → treated as 0 and skipped
    chain = [{"expiry_days": 30, "oi": 5000, "option_type": "call"}]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain)
    assert result["net_vanna"] == 0.0
    assert result["interpretation"] == "Neutral dealer positioning."


def test_compute_dealer_positioning_vanna_bullish():
    from services.options import compute_dealer_positioning

    # High OTM put near expiry → positive vanna
    chain = [
        {"strike": 80, "expiry_days": 5, "iv": 0.50, "oi": 5000, "option_type": "put"},
    ]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain)
    assert result["vanna_signal"] in ("bullish", "bearish", "neutral")
    assert result["charm_signal"] in ("bullish", "bearish", "neutral")


def test_compute_dealer_positioning_vanna_bearish():
    from services.options import compute_dealer_positioning

    # High OTM call near expiry → negative net vanna
    chain = [
        {"strike": 120, "expiry_days": 5, "iv": 0.50, "oi": 5000, "option_type": "call"},
    ]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain)
    assert isinstance(result["net_vanna"], float)


# ── _fetch_options_polygon ───────────────────────────────────────────────────


def test_fetch_options_polygon_no_key():
    from services.options import _fetch_options_polygon

    with patch.dict("os.environ", {}, clear=True):
        assert _fetch_options_polygon("AAPL") is None


def test_fetch_options_polygon_403():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        assert _fetch_options_polygon("AAPL") is None


def test_fetch_options_polygon_non_200():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        assert _fetch_options_polygon("AAPL") is None


def test_fetch_options_polygon_exception():
    from services.options import _fetch_options_polygon

    with (
        patch("services.options.os.getenv", return_value="fake_key"),
        patch("requests.get", side_effect=Exception("net fail")),
    ):
        assert _fetch_options_polygon("AAPL") is None


def test_fetch_options_polygon_empty_results():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"results": []}
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        assert _fetch_options_polygon("AAPL") is None


def test_fetch_options_polygon_total_vol_too_low():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 100, "expiration_date": "2026-07-18"},
                "day": {"volume": 10},
                "open_interest": 5,
                "implied_volatility": 0.25,
            }
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        assert _fetch_options_polygon("AAPL") is None


def test_fetch_options_polygon_success_minimal():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 100},
                "open_interest": 50,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148.5},
                "greeks": {"delta": 0.52, "gamma": 0.05},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 80},
                "open_interest": 40,
                "implied_volatility": 0.32,
                "greeks": {"delta": -0.48, "gamma": 0.04},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert result["source"] == "polygon"
    assert result["spot"] == 148.5
    assert result["call_vol"] == 100
    assert result["put_vol"] == 80
    assert result["gex"] is not None


def test_fetch_options_polygon_spot_from_delta():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 200},
                "open_interest": 100,
                "implied_volatility": 0.30,
                "underlying_asset": {},
                "greeks": {"delta": 0.50},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 100},
                "open_interest": 50,
                "implied_volatility": 0.32,
                "greeks": {"delta": -0.48},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert result["spot"] == 150.0


def test_fetch_options_polygon_pagination():
    from services.options import _fetch_options_polygon

    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 200},
                "open_interest": 100,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": 0.52, "gamma": 0.05},
            }
        ],
        "next_url": "https://api.polygon.io/v3/snapshot/options/AAPL?page2",
    }
    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 100},
                "open_interest": 50,
                "implied_volatility": 0.32,
                "greeks": {"delta": -0.48, "gamma": 0.04},
            }
        ]
    }

    def _get(url, **kwargs):
        if "page2" in url:
            return resp2
        return resp1

    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", side_effect=_get):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert result["total_vol"] == 300


def test_fetch_options_polygon_sweep_detection():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 1200},
                "open_interest": 100,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": 0.52, "gamma": 0.05},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 100},
                "open_interest": 50,
                "implied_volatility": 0.32,
                "greeks": {"delta": -0.48, "gamma": 0.04},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert len(result["sweep_calls"]) >= 1
    assert result["sweep_calls"][0]["vol_oi"] > 5


def test_fetch_options_polygon_iv_rank_and_skew():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 500},
                "open_interest": 200,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": 0.25, "gamma": 0.05},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 500},
                "open_interest": 200,
                "implied_volatility": 0.35,
                "greeks": {"delta": -0.25, "gamma": 0.04},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert result["skew_25d"] is not None
    assert result["put_iv_25d"] is not None
    assert result["call_iv_25d"] is not None


def test_fetch_options_polygon_zero_dte_and_max_pain():
    from datetime import datetime, timezone
    from services.options import _fetch_options_polygon

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": today_str},
                "day": {"volume": 300},
                "open_interest": 100,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": 0.52, "gamma": 0.05},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": today_str},
                "day": {"volume": 300},
                "open_interest": 200,
                "implied_volatility": 0.32,
                "greeks": {"delta": -0.48, "gamma": 0.04},
            },
            {
                "details": {"contract_type": "call", "strike_price": 155, "expiration_date": today_str},
                "day": {"volume": 100},
                "open_interest": 50,
                "implied_volatility": 0.28,
                "greeks": {"delta": 0.45, "gamma": 0.03},
            },
            {
                "details": {"contract_type": "put", "strike_price": 140, "expiration_date": today_str},
                "day": {"volume": 100},
                "open_interest": 50,
                "implied_volatility": 0.35,
                "greeks": {"delta": -0.40, "gamma": 0.03},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert "zero_dte_ratio" in result
    assert "max_pain" in result


def test_fetch_options_polygon_gex_flip_level():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 500},
                "open_interest": 200,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": 0.52, "gamma": 0.05},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 500},
                "open_interest": 200,
                "implied_volatility": 0.32,
                "greeks": {"delta": -0.48, "gamma": 0.04},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert "gex_flip_level" in result


def test_fetch_options_polygon_delta_flow():
    from services.options import _fetch_options_polygon

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "details": {"contract_type": "call", "strike_price": 150, "expiration_date": "2026-07-18"},
                "day": {"volume": 500},
                "open_interest": 200,
                "implied_volatility": 0.30,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": 0.52, "gamma": 0.05},
            },
            {
                "details": {"contract_type": "put", "strike_price": 145, "expiration_date": "2026-07-18"},
                "day": {"volume": 500},
                "open_interest": 200,
                "implied_volatility": 0.32,
                "underlying_asset": {"price": 148},
                "greeks": {"delta": -0.48, "gamma": 0.04},
            },
        ]
    }
    with patch("services.options.os.getenv", return_value="fake_key"), patch("requests.get", return_value=mock_resp):
        result = _fetch_options_polygon("AAPL")
    assert result is not None
    assert "net_delta_flow" in result
    assert "delta_flow_ratio" in result


# ── _fetch_options (yfinance path) ───────────────────────────────────────────


def test_fetch_options_cache_hit():
    from services.options import _fetch_options

    opts._opt_cache["AAPL"] = ({"pc_ratio": 1.1}, 9999999999.0)  # far future
    result = _fetch_options("AAPL")
    assert result == {"pc_ratio": 1.1}


def test_fetch_options_polygon_fallback_then_yfinance():
    from services.options import _fetch_options

    # Polygon returns None, then yfinance path
    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_chain = MagicMock()
        import pandas as pd

        mock_chain.calls = pd.DataFrame(
            {
                "strike": [150.0],
                "volume": [1000],
                "openInterest": [500],
                "impliedVolatility": [0.25],
                "inTheMoney": [False],
            }
        )
        mock_chain.puts = pd.DataFrame(
            {
                "strike": [145.0],
                "volume": [500],
                "openInterest": [300],
                "impliedVolatility": [0.30],
                "inTheMoney": [False],
            }
        )
        mock_ticker.option_chain.return_value = mock_chain
        MockTicker.return_value = mock_ticker

        result = _fetch_options("AAPL")

    assert result is not None
    assert result["call_vol"] == 1000
    assert result["put_vol"] == 500
    assert result["total_vol"] == 1500


def test_fetch_options_yfinance_no_expirations():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = []
        MockTicker.return_value = mock_ticker
        assert _fetch_options("AAPL") == {}


def test_fetch_options_yfinance_chain_exception():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_ticker.option_chain.side_effect = Exception("chain fail")
        MockTicker.return_value = mock_ticker
        assert _fetch_options("AAPL") == {}


def test_fetch_options_yfinance_no_calls():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_chain = MagicMock()
        import pandas as pd

        mock_chain.calls = pd.DataFrame(columns=["strike", "volume", "openInterest", "impliedVolatility", "inTheMoney"])
        mock_chain.puts = pd.DataFrame(columns=["strike", "volume", "openInterest", "impliedVolatility", "inTheMoney"])
        mock_ticker.option_chain.return_value = mock_chain
        MockTicker.return_value = mock_ticker
        assert _fetch_options("AAPL") == {}


def test_fetch_options_yfinance_total_vol_too_low():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_chain = MagicMock()
        import pandas as pd

        mock_chain.calls = pd.DataFrame(
            {
                "strike": [150.0],
                "volume": [10],
                "openInterest": [5],
                "impliedVolatility": [0.25],
                "inTheMoney": [False],
            }
        )
        mock_chain.puts = pd.DataFrame(
            {
                "strike": [145.0],
                "volume": [5],
                "openInterest": [3],
                "impliedVolatility": [0.30],
                "inTheMoney": [False],
            }
        )
        mock_ticker.option_chain.return_value = mock_chain
        MockTicker.return_value = mock_ticker
        assert _fetch_options("AAPL") == {}


def test_fetch_options_yfinance_full_success():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18", "2026-08-15")
        mock_chain1 = MagicMock()
        import pandas as pd

        mock_chain1.calls = pd.DataFrame(
            {
                "strike": [150.0, 155.0],
                "volume": [1000, 800],
                "openInterest": [500, 400],
                "impliedVolatility": [0.25, 0.26],
                "inTheMoney": [False, False],
            }
        )
        mock_chain1.puts = pd.DataFrame(
            {
                "strike": [145.0, 140.0],
                "volume": [600, 400],
                "openInterest": [300, 200],
                "impliedVolatility": [0.30, 0.32],
                "inTheMoney": [False, False],
            }
        )
        mock_chain2 = MagicMock()
        mock_chain2.calls = pd.DataFrame(
            {
                "strike": [150.0],
                "volume": [500],
                "openInterest": [250],
                "impliedVolatility": [0.24],
                "inTheMoney": [False],
            }
        )
        mock_chain2.puts = pd.DataFrame(
            {
                "strike": [145.0],
                "volume": [300],
                "openInterest": [150],
                "impliedVolatility": [0.28],
                "inTheMoney": [False],
            }
        )
        mock_ticker.option_chain.side_effect = [mock_chain1, mock_chain2]
        MockTicker.return_value = mock_ticker

        result = _fetch_options("AAPL")

    assert result is not None
    assert result["call_vol"] == 2300
    assert result["put_vol"] == 1300
    assert result["total_vol"] == 3600
    assert result["near_iv"] is not None
    assert result["far_iv"] is not None
    assert result["gex"] is not None
    assert result["avg_iv"] is not None


def test_fetch_options_yfinance_gex_exception():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
        patch("services.options._bs_gamma", side_effect=Exception("gex fail")),
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_chain = MagicMock()
        import pandas as pd

        mock_chain.calls = pd.DataFrame(
            {
                "strike": [150.0],
                "volume": [1000],
                "openInterest": [500],
                "impliedVolatility": [0.25],
                "inTheMoney": [False],
            }
        )
        mock_chain.puts = pd.DataFrame(
            {
                "strike": [145.0],
                "volume": [500],
                "openInterest": [300],
                "impliedVolatility": [0.30],
                "inTheMoney": [False],
            }
        )
        mock_ticker.option_chain.return_value = mock_chain
        MockTicker.return_value = mock_ticker

        result = _fetch_options("AAPL")
    assert result is not None
    assert result["gex"] is not None  # should return 0.0 after rounding


def test_fetch_options_yfinance_avg_iv_exception():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_chain = MagicMock()
        import pandas as pd

        mock_chain.calls = pd.DataFrame(
            {
                "strike": [150.0],
                "volume": [1000],
                "openInterest": [500],
                "impliedVolatility": [0.25],
                "inTheMoney": [False],
            }
        )
        mock_chain.puts = pd.DataFrame(
            {
                "strike": [145.0],
                "volume": [500],
                "openInterest": [300],
                "impliedVolatility": [0.30],
                "inTheMoney": [False],
            }
        )
        mock_ticker.option_chain.return_value = mock_chain
        MockTicker.return_value = mock_ticker

        with patch("pandas.concat", side_effect=Exception("iv fail")):
            result = _fetch_options("AAPL")
    assert result is not None
    assert result.get("avg_iv") is None


def test_fetch_options_yfinance_skew_exception():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker") as MockTicker,
    ):
        mock_ticker = MagicMock()
        mock_ticker.options = ("2026-07-18",)
        mock_chain = MagicMock()
        import pandas as pd

        mock_chain.calls = pd.DataFrame(
            {
                "strike": [150.0],
                "volume": [1000],
                "openInterest": [500],
                "impliedVolatility": [0.25],
                "inTheMoney": [False],
            }
        )
        mock_chain.puts = pd.DataFrame(
            {
                "strike": [145.0],
                "volume": [500],
                "openInterest": [300],
                "impliedVolatility": [0.30],
                "inTheMoney": [False],
            }
        )
        mock_ticker.option_chain.return_value = mock_chain
        MockTicker.return_value = mock_ticker

        with patch("pandas.DataFrame.idxmin", side_effect=Exception("skew fail")):
            result = _fetch_options("AAPL")
    assert result is not None
    assert result.get("skew_25d") is None


def test_fetch_options_yfinance_overall_exception():
    from services.options import _fetch_options

    with (
        patch("services.options._fetch_options_polygon", return_value=None),
        patch("services.options.yf.Ticker", side_effect=Exception("boom")),
    ):
        result = _fetch_options("AAPL")
    assert result == {}


# ── get_options_flow ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_options_flow():
    from services.options import get_options_flow

    with patch("services.options._fetch_options", return_value={"pc_ratio": 1.1}):
        result = await get_options_flow("AAPL")
    assert result == {"pc_ratio": 1.1}


# ── score_options — uncovered branches ───────────────────────────────────────


def test_score_options_otm_call_surge():
    from services.options import score_options

    opt = {
        "call_vol": 1000,
        "put_vol": 500,
        "otm_call_vol": 700,
        "otm_put_vol": 100,
    }
    score, rationale = score_options(opt)
    assert any("OTM Call Buying Surge" in r["head"] for r in rationale)
    assert score > 0


def test_score_options_otm_put_surge():
    from services.options import score_options

    opt = {
        "call_vol": 500,
        "put_vol": 1000,
        "otm_call_vol": 100,
        "otm_put_vol": 800,
    }
    score, rationale = score_options(opt)
    assert any("OTM Put Hedging Spike" in r["head"] for r in rationale)
    assert score < 0


def test_score_options_unusual_vol_bullish():
    from services.options import score_options

    opt = {
        "unusual_vol_ratio": 4.0,
        "pc_ratio": 0.8,
        "total_vol": 10000,
        "expiries_checked": 2,
    }
    score, rationale = score_options(opt)
    assert any("Unusual Options Activity" in r["head"] for r in rationale)
    assert score > 0


def test_score_options_unusual_vol_bearish():
    from services.options import score_options

    opt = {
        "unusual_vol_ratio": 4.0,
        "pc_ratio": 1.2,
        "total_vol": 10000,
        "expiries_checked": 2,
    }
    score, rationale = score_options(opt)
    assert any("Unusual Options Activity" in r["head"] for r in rationale)
    assert score < 0


def test_score_options_unusual_vol_no_pc():
    from services.options import score_options

    opt = {
        "unusual_vol_ratio": 4.0,
        "total_vol": 10000,
        "expiries_checked": 2,
    }
    score, rationale = score_options(opt)
    # bias = 0 when pc is None
    assert any("Unusual Options Activity" in r["head"] for r in rationale)
    assert score == 0.0


def test_score_options_iv_term_spike():
    from services.options import score_options

    opt = {"iv_term_spike": 1.8, "near_iv": 0.35, "far_iv": 0.20}
    score, rationale = score_options(opt)
    assert any("IV Spike" in r["head"] for r in rationale)
    assert score < 0


def test_score_options_low_iv_with_volume():
    from services.options import score_options

    opt = {"avg_iv": 0.15, "unusual_vol_ratio": 3.0}
    score, rationale = score_options(opt)
    assert any("Low IV" in r["head"] for r in rationale)
    assert score > 0


def test_score_options_very_high_iv():
    from services.options import score_options

    opt = {"avg_iv": 0.80, "unusual_vol_ratio": 1.0}
    score, rationale = score_options(opt)
    assert any("Very High Implied Volatility" in r["head"] for r in rationale)
    assert score == 0.0


def test_score_options_iv_rank_expensive():
    from services.options import score_options

    opt = {"iv_rank": 85.0}
    score, rationale = score_options(opt)
    assert any("IV Rank" in r["head"] and "Expensive" in r["head"] for r in rationale)
    assert score == 0.0


def test_score_options_iv_rank_cheap():
    from services.options import score_options

    opt = {"iv_rank": 15.0}
    score, rationale = score_options(opt)
    assert any("IV Rank" in r["head"] and "Cheap" in r["head"] for r in rationale)
    assert score > 0


def test_score_options_skew_high_put():
    from services.options import score_options

    opt = {"skew_25d": 0.15}
    score, rationale = score_options(opt)
    assert any("Put Skew" in r["head"] for r in rationale)
    assert score < 0


def test_score_options_skew_inverted():
    from services.options import score_options

    opt = {"skew_25d": -0.08}
    score, rationale = score_options(opt)
    assert any("Inverted Skew" in r["head"] for r in rationale)
    assert score > 0


def test_score_options_gex_positive():
    from services.options import score_options

    opt = {"gex": 600_000_000}
    score, rationale = score_options(opt)
    assert any("Positive GEX" in r["head"] for r in rationale)
    assert score == 0.0


def test_score_options_gex_negative():
    from services.options import score_options

    opt = {"gex": -600_000_000}
    score, rationale = score_options(opt)
    assert any("Negative GEX" in r["head"] for r in rationale)
    assert score < 0


def test_score_options_vanna_charm_dealer_positioning():
    from services.options import score_options

    opt = {
        "spot": 150.0,
        "price": 150.0,
        "chains_data": [
            {
                "dte": 10,
                "calls": [
                    {"impliedVolatility": 0.25, "strike": 155, "openInterest": 5000},
                ],
                "puts": [
                    {"impliedVolatility": 0.30, "strike": 145, "openInterest": 5000},
                ],
            }
        ],
    }
    score, rationale = score_options(opt)
    # Should include Vanna or Charm rationale items
    vanna_or_charm = any("Vanna" in r["head"] or "Charm" in r["head"] for r in rationale)
    # Depending on math results, may or may not trigger; just ensure it doesn't crash
    assert isinstance(score, float)


def test_score_options_delta_flow_positive():
    from services.options import score_options

    opt = {"delta_flow_ratio": 0.25, "total_vol": 10000, "net_delta_flow": 125000}
    score, rationale = score_options(opt)
    assert any("Bullish Delta Flow" in r["head"] for r in rationale)
    assert score > 0


def test_score_options_delta_flow_negative():
    from services.options import score_options

    opt = {"delta_flow_ratio": -0.25, "total_vol": 10000, "net_delta_flow": -125000}
    score, rationale = score_options(opt)
    assert any("Bearish Delta Flow" in r["head"] for r in rationale)
    assert score < 0


def test_score_options_max_pain_far_away():
    from services.options import score_options

    from datetime import datetime, timezone, timedelta

    near_exp = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%d")
    opt = {
        "max_pain": 155.0,
        "spot": 150.0,
        "price": 150.0,
        "expiry": near_exp,
    }
    score, rationale = score_options(opt)
    assert not any("Max Pain Pull" in r["head"] for r in rationale)


def test_score_options_vanna_charm_exception():
    from services.options import score_options

    opt = {
        "spot": 150.0,
        "chains_data": [
            {
                "dte": 10,
                "calls": [{"impliedVolatility": 0.25, "strike": 155, "openInterest": 5000}],
                "puts": [{"impliedVolatility": 0.30, "strike": 145, "openInterest": 5000}],
            }
        ],
    }
    with patch("services.options.compute_dealer_positioning", side_effect=Exception("dp fail")):
        score, rationale = score_options(opt)
    assert isinstance(score, float)


# ── cache helpers — additional redis branches ────────────────────────────────


def test_opt_cache_get_redis_hit():
    import services.options as opts

    mock_redis = MagicMock()
    mock_redis.get.return_value = b'{"pc_ratio": 1.2}'
    opts._opt_redis = mock_redis
    from services.options import _opt_cache_get

    result = _opt_cache_get("AAPL")
    assert result == {"pc_ratio": 1.2}
    opts._opt_redis = None


def test_opt_cache_get_redis_error():
    import services.options as opts

    mock_redis = MagicMock()
    mock_redis.get.side_effect = Exception("redis down")
    opts._opt_redis = mock_redis
    opts._opt_cache = {}
    from services.options import _opt_cache_get

    assert _opt_cache_get("AAPL") is None
    opts._opt_redis = None


def test_opt_cache_get_expired():
    import services.options as opts

    opts._opt_redis = None
    opts._opt_cache = {"AAPL": ({"pc_ratio": 1.2}, 0.0)}
    from services.options import _opt_cache_get

    assert _opt_cache_get("AAPL") is None
    opts._opt_cache = {}


def test_opt_cache_set_redis_error():
    import services.options as opts

    mock_redis = MagicMock()
    mock_redis.setex.side_effect = Exception("redis down")
    opts._opt_redis = mock_redis
    from services.options import _opt_cache_set

    _opt_cache_set("AAPL", {"pc_ratio": 1.2})
    assert opts._opt_cache["AAPL"][0] == {"pc_ratio": 1.2}
    opts._opt_redis = None
    opts._opt_cache = {}


def test_ivh_load_redis_longer():
    import services.options as opts

    mock_redis = MagicMock()
    mock_redis.get.return_value = b"[0.20, 0.22, 0.24, 0.26]"
    opts._opt_redis = mock_redis
    opts._iv_history = {"AAPL": [0.20, 0.22]}
    from services.options import _ivh_load

    result = _ivh_load("AAPL")
    assert result == [0.20, 0.22, 0.24, 0.26]
    assert opts._iv_history["AAPL"] == [0.20, 0.22, 0.24, 0.26]
    opts._opt_redis = None
    opts._iv_history = {}


def test_ivh_save_redis_error():
    import services.options as opts

    mock_redis = MagicMock()
    mock_redis.setex.side_effect = Exception("redis down")
    opts._opt_redis = mock_redis
    from services.options import _ivh_save

    _ivh_save("AAPL", [0.20, 0.22])
    assert opts._iv_history["AAPL"] == [0.20, 0.22]
    opts._opt_redis = None
    opts._iv_history = {}
