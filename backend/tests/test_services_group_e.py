"""Tests for services/macro.py, services/broker_svc.py, services/edgar.py — uncovered branches."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_df(close_vals):
    import pandas as pd

    idx = pd.date_range("2026-01-01", periods=len(close_vals), freq="D")
    return pd.DataFrame(
        {
            "Close": close_vals,
            "Open": close_vals,
            "High": close_vals,
            "Low": close_vals,
            "Volume": [1e6] * len(close_vals),
        },
        index=idx,
    )


def _make_user(**kwargs):
    u = MagicMock()
    u.id = 1
    u.is_owner = False
    u.subscription_tier = "pro"
    u.subscription_status = "active"
    u.auto_execute = True
    u.auto_execute_broker = "alpaca"
    u.auto_execute_min_conf = 75.0
    u.auto_execute_qty_dollars = 100.0
    u.alpaca_key_enc = None
    u.alpaca_secret_enc = None
    u.alpaca_account_type = "paper"
    u.max_daily_orders = None
    u.max_ticker_notional = None
    for k, v in kwargs.items():
        setattr(u, k, v)
    return u


def _mock_aiohttp_json(json_data, status=200):
    resp = MagicMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


def _mock_aiohttp_text(text_data, status=200):
    resp = MagicMock()
    resp.status = status
    resp.text = AsyncMock(return_value=text_data)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


# ── macro.py: _sector_rotation_stage edge cases ───────────────────────────────


def test_sector_rotation_stage_late_exact():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=25, yc_spread=-0.5, hyg_1m=-1.0, sp500_trend="up")
    assert result["stage"] == "late"
    assert result["confidence"] > 0
    assert "bear_checks" in result


def test_sector_rotation_stage_recession_exact():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=35, yc_spread=-1.0, hyg_1m=-5.0, sp500_trend="down")
    assert result["stage"] == "recession"
    assert result["confidence"] > 0
    assert "XLV" in result["favoured"] or "XLP" in result["favoured"]


def test_sector_rotation_stage_mid_confidence():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=20, yc_spread=0.5, hyg_1m=0.5, sp500_trend="up")
    assert result["stage"] in ("mid", "early")
    assert result["confidence"] >= 0


# ── macro.py: get_macro_context branches ──────────────────────────────────────


@pytest.mark.asyncio
async def test_get_macro_context_vix_spike_and_t10y_high():
    from services.macro import get_macro_context

    mapping = {
        "^VIX": _make_df([28.0, 30.0, 35.0]),
        "^TNX": _make_df([4.5, 4.7, 5.0]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([30.0, 31.0, 32.0]),
        "^VIX9D": _make_df([34.0, 35.0, 36.0]),
        "^MOVE": _make_df([130.0, 140.0, 150.0]),
        "^IRX": _make_df([500.0, 510.0, 520.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("vix") == 35.0
    assert result.get("t10y") == 5.0
    # VIX > 30 and T10Y > 4.8 should produce negative rationale entries
    assert any("VIX Spiked" in r.get("head", "") for r in result.get("rationale", []))
    assert any("10-Y Yield High" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_vix_low_and_t10y_low():
    from services.macro import get_macro_context

    mapping = {
        "^VIX": _make_df([15.0, 14.0, 12.0]),
        "^TNX": _make_df([3.8, 3.6, 3.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([14.0, 13.0, 12.0]),
        "^VIX9D": _make_df([11.0, 10.0, 9.0]),
        "^MOVE": _make_df([100.0, 95.0, 80.0]),
        "^IRX": _make_df([200.0, 210.0, 220.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("vix") == 12.0
    assert result.get("t10y") == 3.4
    assert any("VIX Low" in r.get("head", "") for r in result.get("rationale", []))
    assert any("10-Y Yield Low" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_sp500_down_and_sma200():
    from services.macro import get_macro_context

    closes = [4500.0] * 200 + [4300.0] * 52
    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df(closes),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("sp500_trend") == "down"
    assert any("S&P 500 Below 50-DMA" in r.get("head", "") for r in result.get("rationale", []))
    assert result.get("sp500_sma200") is not None
    assert result.get("sp500_neutral_zone") in (True, False)


@pytest.mark.asyncio
async def test_get_macro_context_fred_comprehensive():
    from services.macro import get_macro_context

    async def _mock_fred(series_id, api_key):
        values = {
            "FEDFUNDS": 5.5,
            "CPIAUCSL": 300.0,
            "BAMLH0A0HYM2": 6.5,
            "BAMLC0A0CM": 2.5,
            "STLFSI4": 1.5,
            "ICSA": 400000.0,
            "UMCSENT": 55.0,
            "T10Y3M": -0.6,
            "NFCI": 0.0,
            "BAA10Y": 1.0,
        }
        return values.get(series_id)

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    fake_settings = MagicMock()
    fake_settings.fred_api_key = "fake_key"

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro._fred", side_effect=_mock_fred),
        patch("config.get_settings", return_value=fake_settings),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("fed_funds") == 5.5
    assert result.get("hy_spread") == 650.0
    rationale_heads = [r.get("head", "") for r in result.get("rationale", [])]
    assert any("Fed Funds Rate" in h for h in rationale_heads)
    assert any("HY Credit Spread Crisis" in h for h in rationale_heads)
    assert any("IG Credit Spread Stressed" in h for h in rationale_heads)
    assert any("Financial Stress Crisis" in h for h in rationale_heads)
    assert any("Jobless Claims Stress" in h for h in rationale_heads)
    assert any("Consumer Sentiment Distressed" in h for h in rationale_heads)
    assert any("Yield Curve Inverted (T10Y3M" in h for h in rationale_heads)


@pytest.mark.asyncio
async def test_get_macro_context_vix_term_and_vix9d():
    from services.macro import get_macro_context

    mapping = {
        "^VIX": _make_df([18.0, 20.0, 22.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([18.0, 18.5, 19.0]),
        "^VIX9D": _make_df([24.0, 25.0, 26.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    # VIX=22, VIX3M=19 → ratio=1.157 > 1.10 (backwardation)
    assert result.get("vix_term_ratio") is not None
    assert any("VIX Backwardation" in r.get("head", "") for r in result.get("rationale", []))
    # VIX9D=26, VIX=22 → ratio=1.18 > 1.10
    assert result.get("vix9d_ratio") is not None
    assert any("Near-Term Event Risk Elevated" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_move_index():
    from services.macro import get_macro_context

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([130.0, 140.0, 150.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("move") == 150.0
    assert any("Treasury Volatility Stress" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_yield_curve_inverted():
    # t2y is sourced from FRED's DGS2 (real constant-maturity 2-Year Treasury
    # yield), not from ^IRX (the 13-week T-bill) — see macro.py's "Yield
    # curve" section. So triggering an inversion in this test means mocking
    # _fred("DGS2", ...) above the mocked ^TNX (10Y) level, the same way
    # test_get_macro_context_fred_comprehensive mocks _fred for the other
    # FRED-sourced series, rather than mocking ^IRX (which this section no
    # longer reads at all).
    from services.macro import get_macro_context

    async def _mock_fred(series_id, api_key):
        values = {"DGS2": 5.0}
        return values.get(series_id)

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([3.5, 3.4, 3.3]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    fake_settings = MagicMock()
    fake_settings.fred_api_key = "fake_key"

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro._fred", side_effect=_mock_fred),
        patch("config.get_settings", return_value=fake_settings),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("t2y") == 5.0
    assert result.get("yc_spread") is not None
    assert result.get("yc_spread") < 0
    assert any("Yield Curve Inverted" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_copper_gold():
    from services.macro import get_macro_context

    # Need iloc[-1] != iloc[-21]; use 22 old values + 1 new value so -21 falls in old block
    cu_vals = [3.8] * 22 + [4.0]
    au_vals = [2000.0] * 22 + [2000.0]

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df(cu_vals),
        "GC=F": _make_df(au_vals),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("cu_gold_1m") is not None
    assert any("Copper/Gold Ratio Rising" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_cross_asset_headwinds_three():
    from services.macro import get_macro_context

    tlt = [90.0] * 5 + [92.0]  # +2.2%
    uup = [26.0] * 5 + [26.5]  # +1.9%
    xle = [80.0] * 5 + [76.0]  # -5.0%

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df(tlt),
        "UUP": _make_df(uup),
        "XLE": _make_df(xle),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("cross_asset_headwinds") == 3
    assert any("Cross-Asset Macro Breakdown" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_cross_asset_headwinds_zero():
    from services.macro import get_macro_context

    tlt = [90.0] * 6
    uup = [26.0] * 6
    xle = [80.0] * 6

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df(tlt),
        "UUP": _make_df(uup),
        "XLE": _make_df(xle),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("cross_asset_headwinds") == 0
    assert any("Clean Macro Backdrop" in r.get("head", "") for r in result.get("rationale", []))


@pytest.mark.asyncio
async def test_get_macro_context_t10y_changes_and_spread():
    from services.macro import get_macro_context

    tnx_3mo = [4.0] * 22 + [4.5]
    irx_5d = [300.0, 310.0, 320.0, 330.0, 340.0]

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df(tnx_3mo),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df(irx_5d),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value=""),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("t10y_30d_chg") is not None
    assert result.get("t10y2y_spread") is not None


@pytest.mark.asyncio
async def test_get_macro_context_market_status_polygon():
    from services.macro import get_macro_context

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    market_resp = MagicMock()
    market_resp.status = 200
    market_resp.json = AsyncMock(return_value={"exchanges": {"nyse": "open"}, "afterHours": False, "earlyHours": False})
    market_cm = MagicMock()
    market_cm.__aenter__ = AsyncMock(return_value=market_resp)
    market_cm.__aexit__ = AsyncMock(return_value=False)

    mock_sess = MagicMock()
    mock_sess.get = MagicMock(return_value=market_cm)
    mock_shared = MagicMock()
    mock_shared.__aenter__ = AsyncMock(return_value=mock_sess)
    mock_shared.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value="poly_key"),
        patch("services.macro.shared_session", return_value=mock_shared),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert result.get("market_open") is True
    assert result.get("after_hours") is False


@pytest.mark.asyncio
async def test_get_macro_context_market_status_fallback():
    from services.macro import get_macro_context

    mapping = {
        "^VIX": _make_df([18.0, 19.0, 20.0]),
        "^TNX": _make_df([4.2, 4.3, 4.4]),
        "^GSPC": _make_df([4700.0] * 252),
        "HYG": _make_df([77.0] * 66),
        "^VIX3M": _make_df([20.0, 21.0, 22.0]),
        "^VIX9D": _make_df([21.0, 22.0, 23.0]),
        "^MOVE": _make_df([100.0, 105.0, 110.0]),
        "^IRX": _make_df([400.0, 410.0, 420.0]),
        "DX-Y.NYB": _make_df([100.0] * 66),
        "HG=F": _make_df([4.0] * 66),
        "GC=F": _make_df([2000.0] * 66),
        "TLT": _make_df([90.0] * 46),
        "UUP": _make_df([26.0] * 46),
        "XLE": _make_df([80.0] * 46),
    }

    async def _mock_history(ticker, **kwargs):
        return mapping.get(ticker)

    # Patch os.getenv to return a polygon key so the code enters the if block,
    # then force shared_session to raise so the except fallback runs.
    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
        patch("services.macro.os.getenv", return_value="poly_key"),
        patch("services.macro.shared_session", side_effect=Exception("network down")),
    ):
        result = await get_macro_context()

    assert isinstance(result, dict)
    assert "market_open" in result


# ── broker_svc.py ─────────────────────────────────────────────────────────────


def test_current_key_version():
    from services.broker_svc import current_key_version

    assert isinstance(current_key_version(), int)
    assert current_key_version() >= 2


def test_rotate_credential_already_current():
    from services.broker_svc import encrypt_credential, rotate_credential

    plaintext = "my-key"
    token = encrypt_credential(plaintext)
    assert rotate_credential(token) == token


def test_rotate_credential_invalid():
    from services.broker_svc import rotate_credential

    assert rotate_credential("not-a-valid-token") is None


@pytest.mark.asyncio
async def test_verify_ibkr_connection_success():
    from services.broker_svc import verify_ibkr_connection

    fake_account = {"accountId": "U123", "equity": "50000"}
    with patch("services.ibkr_rest.get_account", new_callable=AsyncMock, return_value=fake_account):
        result = await verify_ibkr_connection("key", "secret", live=False)
    assert result["accountId"] == "U123"


@pytest.mark.asyncio
async def test_verify_ibkr_connection_failure():
    from services.broker_svc import verify_ibkr_connection

    with patch("services.ibkr_rest.get_account", new_callable=AsyncMock, side_effect=Exception("timeout")):
        with pytest.raises(ValueError, match="Could not connect to IBKR"):
            await verify_ibkr_connection("key", "secret", live=False)


@pytest.mark.asyncio
async def test_check_portfolio_drawdown_ibkr():
    from services.broker_svc import check_portfolio_drawdown

    user = _make_user()
    bad_account = {"equity": "10000", "unrealized_pl": "-600"}

    with patch("services.ibkr_rest.get_account", new_callable=AsyncMock, return_value=bad_account):
        blocked = await check_portfolio_drawdown(user, "KEY", "SECRET", live=False, broker="ibkr")
    assert blocked is True


@pytest.mark.asyncio
async def test_check_portfolio_drawdown_telegram_alert():
    from services.broker_svc import check_portfolio_drawdown
    import services.telegram_svc as telegram_mod

    user = _make_user()
    bad_account = {"equity": "10000", "unrealized_pl": "-600"}

    with (
        patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=bad_account),
        patch.object(telegram_mod, "send_admin_alert", new_callable=AsyncMock, create=True) as mock_alert,
    ):
        blocked = await check_portfolio_drawdown(user, "KEY", "SECRET", live=False)

    assert blocked is True
    mock_alert.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_portfolio_drawdown_missing_equity():
    from services.broker_svc import check_portfolio_drawdown

    user = _make_user()
    no_equity = {"unrealized_pl": "-100"}

    with patch("services.alpaca_rest.get_account", new_callable=AsyncMock, return_value=no_equity):
        blocked = await check_portfolio_drawdown(user, "KEY", "SECRET", live=False)
    assert blocked is True


@pytest.fixture(autouse=True)
def _patch_broker_accounts_for_group_e():
    """Provide healthy broker accounts so drawdown fail-closed logic doesn't block tests."""
    with (
        patch(
            "services.alpaca_rest.get_account",
            new_callable=AsyncMock,
            return_value={"equity": "10000.00", "unrealized_pl": "0.00"},
        ),
        patch(
            "services.ibkr_rest.get_account",
            new_callable=AsyncMock,
            return_value={"equity": "10000.00", "unrealized_pl": "0.00"},
        ),
    ):
        yield


@pytest.mark.asyncio
async def test_reconcile_broker_orders_no_pending():
    from services.broker_svc import reconcile_broker_orders

    db = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=execute_result)

    result = await reconcile_broker_orders(db)

    assert result == {"checked": 0, "updated": 0, "orphaned": 0, "users": 0}


@pytest.mark.asyncio
async def test_reconcile_broker_orders_updates_and_orphans():
    from services.broker_svc import encrypt_credential, reconcile_broker_orders

    order_filled = MagicMock()
    order_filled.user_id = 1
    order_filled.alpaca_order_id = "order-filled"
    order_filled.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
    order_filled.status = "submitted"

    order_orphan = MagicMock()
    order_orphan.user_id = 1
    order_orphan.alpaca_order_id = "order-orphan"
    order_orphan.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=25)
    order_orphan.status = "submitted"

    user = MagicMock()
    user.id = 1
    user.alpaca_key_enc = encrypt_credential("key")
    user.alpaca_secret_enc = encrypt_credential("secret")
    user.auto_execute_broker = "alpaca"
    user.alpaca_account_type = "paper"

    db = AsyncMock()
    pending_result = MagicMock()
    pending_result.scalars.return_value.all.return_value = [order_filled, order_orphan]
    db.execute = AsyncMock(return_value=pending_result)
    db.get = AsyncMock(return_value=user)

    broker_orders = [{"id": "order-filled", "status": "filled"}]

    with (
        patch("services.alpaca_rest.get_orders", new_callable=AsyncMock, return_value=broker_orders),
        patch("services.tca_service.record_fill_tca", new_callable=AsyncMock),
    ):
        result = await reconcile_broker_orders(db)

    assert result["checked"] == 2
    assert result["updated"] == 1
    assert result["orphaned"] == 1
    assert order_filled.status == "filled"
    assert order_orphan.status == "orphan"
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_check_runtime_risk_limits_daily_orders():
    from services.broker_svc import check_runtime_risk_limits

    user = _make_user()
    user.max_daily_orders = 3

    count_result = MagicMock()
    count_result.scalar.return_value = 3
    db = AsyncMock()
    db.execute = AsyncMock(return_value=count_result)

    result = await check_runtime_risk_limits(user, "AAPL", 100.0, db)
    assert result is not None
    assert "max_daily_orders reached" in result


@pytest.mark.asyncio
async def test_check_runtime_risk_limits_ticker_notional():
    from services.broker_svc import check_runtime_risk_limits

    user = _make_user()
    user.max_ticker_notional = 1000.0

    sum_result = MagicMock()
    sum_result.scalar.return_value = 900.0
    db = AsyncMock()
    db.execute = AsyncMock(return_value=sum_result)

    result = await check_runtime_risk_limits(user, "AAPL", 200.0, db)
    assert result is not None
    assert "max_ticker_notional exceeded" in result


@pytest.mark.asyncio
async def test_execute_signal_bracket_order():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_qty_dollars=200.0,
    )
    db = AsyncMock()
    fake_order = {"id": "bracket-1", "status": "accepted"}

    sig = {
        "ticker": "AAPL",
        "action": "BUY",
        "stopPrice": 150.0,
        "targetPrice": 200.0,
        "entry": 170.0,
        "confidence": 100.0,
    }

    with patch("services.alpaca_rest.submit_bracket_stop_order", new_callable=AsyncMock, return_value=fake_order):
        await execute_signal_for_user(user, sig, 42, db)

    db.add.assert_called_once()
    order_record = db.add.call_args[0][0]
    assert order_record.symbol == "AAPL"
    # Raw Alpaca statuses (e.g. "accepted") are normalized to the broker_orders
    # CheckConstraint vocabulary, not stored verbatim.
    assert order_record.status == "submitted"
    assert order_record.alpaca_order_id == "bracket-1"


@pytest.mark.asyncio
async def test_execute_signal_sell_side():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
    )
    db = AsyncMock()
    fake_order = {"id": "sell-1", "status": "accepted"}

    with patch("services.alpaca_rest.place_notional_order", new_callable=AsyncMock, return_value=fake_order):
        await execute_signal_for_user(user, {"ticker": "TSLA", "action": "SELL", "confidence": 100.0}, 7, db)

    db.add.assert_called_once()
    order_record = db.add.call_args[0][0]
    assert order_record.side == "sell"


@pytest.mark.asyncio
async def test_execute_signal_ibkr():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=None,
        auto_execute_broker="ibkr",
        alpaca_account_type="paper",
    )
    db = AsyncMock()
    fake_order = {"id": "ibkr-1", "status": "accepted"}

    with patch("services.ibkr_rest.place_notional_order", new_callable=AsyncMock, return_value=fake_order):
        await execute_signal_for_user(user, {"ticker": "AAPL", "action": "BUY", "confidence": 100.0}, 1, db)

    db.add.assert_called_once()
    order_record = db.add.call_args[0][0]
    assert order_record.broker == "ibkr"


@pytest.mark.asyncio
async def test_execute_signal_risk_limit_block():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
    )
    db = AsyncMock()

    with patch("services.broker_svc.check_runtime_risk_limits", new_callable=AsyncMock, return_value="blocked"):
        await execute_signal_for_user(user, {"ticker": "AAPL", "action": "BUY", "confidence": 100.0}, None, db)

    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_execute_signal_capacity_block():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
    )
    db = AsyncMock()

    with patch("services.tca_service.check_capacity_limits", new_callable=AsyncMock, return_value=(True, 0.0, 5.0)):
        await execute_signal_for_user(user, {"ticker": "AAPL", "action": "BUY", "confidence": 100.0}, None, db)

    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_execute_signal_capacity_resize():
    from services.broker_svc import encrypt_credential, execute_signal_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_qty_dollars=100.0,
    )
    db = AsyncMock()
    fake_order = {"id": "resized-1", "status": "accepted"}

    with (
        patch("services.tca_service.check_capacity_limits", new_callable=AsyncMock, return_value=(False, 50.0, 1.0)),
        patch(
            "services.alpaca_rest.place_notional_order", new_callable=AsyncMock, return_value=fake_order
        ) as mock_place,
    ):
        await execute_signal_for_user(user, {"ticker": "AAPL", "action": "BUY", "confidence": 100.0}, None, db)

    db.add.assert_called_once()
    call_kwargs = mock_place.call_args
    notional = call_kwargs.kwargs.get("notional") or call_kwargs[1].get("notional")
    assert notional == 50.0


@pytest.mark.asyncio
async def test_execute_portfolio_for_user_success():
    from services.broker_svc import encrypt_credential, execute_portfolio_for_user

    user = _make_user(
        alpaca_key_enc=encrypt_credential("KEY"),
        alpaca_secret_enc=encrypt_credential("SECRET"),
        alpaca_account_type="paper",
        auto_execute_qty_dollars=100.0,
    )

    pnl_result = MagicMock()
    pnl_result.scalar_one_or_none.return_value = None
    db = AsyncMock()
    db.execute = AsyncMock(return_value=pnl_result)
    db.flush = AsyncMock()

    active_signals = [
        {"ticker": "AAPL", "action": "BUY", "entry": 170.0, "price": 170.0, "stopPrice": 150.0, "targetPrice": 200.0}
    ]

    with (
        patch("services.broker_svc.check_portfolio_drawdown", new_callable=AsyncMock, return_value=False),
        patch(
            "services.alpaca_rest.get_account",
            new_callable=AsyncMock,
            return_value={"equity": "50000", "unrealized_pl": "1000", "cash": "25000"},
        ),
        patch(
            "services.portfolio_allocator.allocate_portfolio",
            new_callable=AsyncMock,
            return_value=[
                {"ticker": "AAPL", "action": "BUY", "notional": 1000.0, "target_weight": 0.1, "signal_id": 1}
            ],
        ),
        patch("services.broker_svc.check_runtime_risk_limits", new_callable=AsyncMock, return_value=None),
        patch("services.tca_service.check_capacity_limits", new_callable=AsyncMock, return_value=(False, 1000.0, 0.0)),
        patch(
            "services.alpaca_rest.place_notional_order",
            new_callable=AsyncMock,
            return_value={"id": "ord1", "status": "accepted"},
        ),
        patch("services.provider_telemetry.current_cycle_id", MagicMock(get=lambda: "cycle-1")),
    ):
        await execute_portfolio_for_user(user, active_signals, db)

    db.add.assert_called()
    db.flush.assert_awaited()


# ── edgar.py ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_edgar_globals():
    import services.edgar as ed

    orig_cik_map = dict(ed._cik_map)
    orig_cik_map_ts = ed._cik_map_ts
    orig_mda_cache = dict(ed._mda_cache)
    orig_activity_cache = dict(ed._activity_cache)
    orig_buyback_cache = dict(ed._buyback_cache)
    yield
    ed._cik_map = orig_cik_map
    ed._cik_map_ts = orig_cik_map_ts
    ed._mda_cache = orig_mda_cache
    ed._activity_cache = orig_activity_cache
    ed._buyback_cache = orig_buyback_cache


@pytest.mark.asyncio
async def test_ensure_cik_map_and_get_cik():
    import services.edgar as ed

    ed._cik_map_ts = 0.0
    ed._cik_map = dict(ed._KNOWN_CIKS)

    mock_json = {"0": {"ticker": "NEWTK", "cik_str": "1234567"}}

    sub_cm = _mock_aiohttp_json(mock_json)
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=sub_cm)
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=mock_session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=session_cm), patch("aiohttp.TCPConnector"):
        cik = await ed._get_cik("NEWTK")

    assert cik == "0001234567"
    assert ed._cik_map_ts > 0


@pytest.mark.asyncio
async def test_get_insider_activity_full_fetch():
    from services.edgar import get_insider_activity

    from datetime import date

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    subs_json = {
        "filings": {
            "recent": {
                "form": ["4", "4", "10-Q"],
                "filingDate": [today, yesterday, "2026-04-01"],
                "accessionNumber": ["000-1", "000-2", "000-3"],
                "primaryDocument": ["form4-1.xml", "form4-2.xml", "10q.html"],
            }
        }
    }

    xml1 = _make_form4_xml([("A", 1000, 150.0)])
    xml2 = _make_form4_xml([("D", 500, 160.0)])

    # Build session that returns submissions then two XML docs
    sub_cm = _mock_aiohttp_json(subs_json)
    xml1_cm = _mock_aiohttp_text(xml1)
    xml2_cm = _mock_aiohttp_text(xml2)

    mock_session = MagicMock()
    mock_session.get = MagicMock(side_effect=[sub_cm, xml1_cm, xml2_cm])
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=mock_session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("aiohttp.ClientSession", return_value=session_cm),
        patch("aiohttp.TCPConnector"),
        patch("services.edgar.cache_get", new_callable=AsyncMock, return_value=None),
        patch("services.edgar.cache_set", new_callable=AsyncMock),
    ):
        result = await get_insider_activity("AAPL")

    assert isinstance(result, dict)
    assert result["buys"] == 1000
    assert result["sells"] == 500
    assert result["filings"] == 2
    assert result["unique_buyers"] == 1


@pytest.mark.asyncio
async def test_fetch_filing_text_success():
    from services.edgar import _fetch_filing_text

    subs_json = {
        "filings": {
            "recent": {
                "form": ["10-Q"],
                "accessionNumber": ["000-123-456"],
                "filingDate": ["2026-05-01"],
            }
        }
    }
    idx_json = {"directory": {"item": [{"name": "doc.html"}]}}
    html = "<html><body>Management Discussion and Analysis " + "Risk factors " * 100 + "</body></html>"

    sub_cm = _mock_aiohttp_json(subs_json)
    idx_cm = _mock_aiohttp_json(idx_json)
    doc_cm = _mock_aiohttp_text(html)

    mock_sess = MagicMock()
    mock_sess.get = MagicMock(side_effect=[sub_cm, idx_cm, doc_cm])
    mock_shared = MagicMock()
    mock_shared.__aenter__ = AsyncMock(return_value=mock_sess)
    mock_shared.__aexit__ = AsyncMock(return_value=False)

    with patch("services.edgar.shared_session", return_value=mock_shared):
        texts = await _fetch_filing_text("0000320193", "10-Q")

    assert isinstance(texts, list)
    assert len(texts) == 1
    assert "Management Discussion and Analysis" in texts[0]


@pytest.mark.asyncio
async def test_get_mda_delta_full_fetch():
    from services.edgar import get_mda_delta

    # Need 2 filings for 10-Q
    subs_json = {
        "filings": {
            "recent": {
                "form": ["10-Q", "10-Q"],
                "accessionNumber": ["000-123-456", "000-789-012"],
                "filingDate": ["2026-05-01", "2026-02-01"],
            }
        }
    }
    idx_json = {"directory": {"item": [{"name": "doc.html"}]}}
    html_cur = "<html><body>Management Discussion and Analysis growth revenue profit expanding opportunity strong</body></html>"
    html_prev = "<html><body>Management Discussion and Analysis risk uncertainty challenges</body></html>"

    sub_cm = _mock_aiohttp_json(subs_json)
    idx1_cm = _mock_aiohttp_json(idx_json)
    doc1_cm = _mock_aiohttp_text(html_cur)
    idx2_cm = _mock_aiohttp_json(idx_json)
    doc2_cm = _mock_aiohttp_text(html_prev)

    mock_sess = MagicMock()
    mock_sess.get = MagicMock(side_effect=[sub_cm, idx1_cm, doc1_cm, idx2_cm, doc2_cm])
    mock_shared = MagicMock()
    mock_shared.__aenter__ = AsyncMock(return_value=mock_sess)
    mock_shared.__aexit__ = AsyncMock(return_value=False)

    with patch("services.edgar.shared_session", return_value=mock_shared):
        result = await get_mda_delta("AAPL")

    assert isinstance(result, dict)
    assert "score" in result
    assert "reason" in result
    assert result["form_type"] == "10-Q"


@pytest.mark.asyncio
async def test_has_active_buyback_true():
    from services.edgar import has_active_buyback

    subs_json = {
        "filings": {
            "recent": {
                "form": ["8-K"],
                "filingDate": ["2026-05-01"],
                "accessionNumber": ["000-123"],
                "primaryDocument": ["8k.html"],
                "items": ["8.01"],
            }
        }
    }
    html = "The company announced a new share repurchase program authorized by the board"

    sub_cm = _mock_aiohttp_json(subs_json)
    doc_cm = _mock_aiohttp_text(html)

    mock_session = MagicMock()
    mock_session.get = MagicMock(side_effect=[sub_cm, doc_cm])
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=mock_session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("aiohttp.ClientSession", return_value=session_cm),
        patch("aiohttp.TCPConnector"),
    ):
        result = await has_active_buyback("AAPL")

    assert result is True


@pytest.mark.asyncio
async def test_has_active_buyback_false():
    from services.edgar import has_active_buyback

    subs_json = {
        "filings": {
            "recent": {
                "form": ["8-K"],
                "filingDate": ["2026-05-01"],
                "accessionNumber": ["000-123"],
                "primaryDocument": ["8k.html"],
                "items": ["8.01"],
            }
        }
    }
    html = "Regular quarterly earnings report with no special announcements"

    sub_cm = _mock_aiohttp_json(subs_json)
    doc_cm = _mock_aiohttp_text(html)

    mock_session = MagicMock()
    mock_session.get = MagicMock(side_effect=[sub_cm, doc_cm])
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=mock_session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("aiohttp.ClientSession", return_value=session_cm),
        patch("aiohttp.TCPConnector"),
    ):
        result = await has_active_buyback("AAPL")

    assert result is False


# ── Helper for Form 4 XML ─────────────────────────────────────────────────────


def _make_form4_xml(transactions):
    import xml.etree.ElementTree as ET

    root = ET.Element("ownershipDocument")
    for code, shares, price in transactions:
        t = ET.SubElement(root, "nonDerivativeTransaction")
        code_el = ET.SubElement(t, "transactionAcquiredDisposedCode")
        ET.SubElement(code_el, "value").text = code
        shares_el = ET.SubElement(t, "transactionShares")
        ET.SubElement(shares_el, "value").text = str(shares)
        price_el = ET.SubElement(t, "transactionPricePerShare")
        ET.SubElement(price_el, "value").text = str(price)
    return ET.tostring(root, encoding="unicode")
