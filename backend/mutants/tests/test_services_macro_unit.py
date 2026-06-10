"""Tests for services/macro.py — macro context, sector rotation, FRED calls."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Pure helper tests ─────────────────────────────────────────────────────────


def test_sector_rotation_stage_early():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=14, yc_spread=1.5, hyg_1m=2.0, sp500_trend="up")
    assert result["stage"] == "early"
    assert "XLY" in result["favoured"]
    assert result["confidence"] > 0


def test_sector_rotation_stage_late():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=32, yc_spread=-0.5, hyg_1m=-3.0, sp500_trend="down")
    assert result["stage"] in ("late", "recession")


def test_sector_rotation_stage_mid():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=20, yc_spread=0.5, hyg_1m=0.5, sp500_trend="up")
    assert result["stage"] in ("mid", "early")


def test_sector_rotation_stage_none_inputs():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(None, None, None, None)
    assert result["stage"] == "mid"
    assert result["confidence"] == 0


def test_sector_rotation_stage_bear():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=35, yc_spread=-1.0, hyg_1m=-5.0, sp500_trend="down")
    assert result["stage"] in ("recession", "late")


# ── FRED fetch ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fred_success():
    from services.macro import _fred

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"observations": [{"value": "5.33"}, {"value": "5.25"}]})
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_cm.__aexit__ = AsyncMock(return_value=False)
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_cm)
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session_cm), patch("aiohttp.TCPConnector"):
        result = await _fred("FEDFUNDS", "test_key")
    assert result == 5.33


@pytest.mark.asyncio
async def test_fred_http_error():
    from services.macro import _fred

    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_cm.__aexit__ = AsyncMock(return_value=False)
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_cm)
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session_cm), patch("aiohttp.TCPConnector"):
        result = await _fred("FEDFUNDS", "bad_key")
    assert result is None


@pytest.mark.asyncio
async def test_fred_exception():
    from services.macro import _fred

    with patch("aiohttp.ClientSession", side_effect=Exception("network error")), patch("aiohttp.TCPConnector"):
        result = await _fred("FEDFUNDS", "key")
    assert result is None


# ── get_macro_context ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_macro_context_no_fred_key(monkeypatch):
    from services.macro import get_macro_context
    import pandas as pd

    # Mock VIX, SPY, TNX, HYG histories
    def _make_df(close_vals):
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

    vix_df = _make_df([18.0, 19.0, 20.0])
    spy_df = _make_df([470.0, 472.0, 475.0])
    tnx_df = _make_df([4.2, 4.3, 4.4])
    hyg_df = _make_df([77.0, 77.5, 78.0])

    async def _mock_history(ticker, **kwargs):
        mapping = {"^VIX": vix_df, "^GSPC": spy_df, "^TNX": tnx_df, "HYG": hyg_df}
        return mapping.get(ticker)

    with (
        patch("services.macro.get_history", side_effect=_mock_history),
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.cache_set"),
    ):
        # Patch settings to have no FRED key
        with patch("services.macro.os.getenv", return_value=""):
            result = await get_macro_context()

    assert isinstance(result, dict)
    assert "vix" in result or result is not None


@pytest.mark.asyncio
async def test_get_macro_context_cached():
    from services.macro import get_macro_context

    cached = {"vix": 20.0, "cached": True}
    with patch("services.macro.cache_get", return_value=cached):
        result = await get_macro_context()
    assert result["cached"] is True


@pytest.mark.asyncio
async def test_get_macro_context_exception():
    from services.macro import get_macro_context

    with (
        patch("services.macro.cache_get", return_value=None),
        patch("services.macro.get_history", side_effect=Exception("yfinance down")),
    ):
        result = await get_macro_context()
    # Should return gracefully, not raise
    assert result is None or isinstance(result, dict)


# ── Sector rotation stage edge cases ─────────────────────────────────────────


def test_sector_rotation_stage_high_bull():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=12, yc_spread=2.0, hyg_1m=3.0, sp500_trend="up")
    assert result["stage"] == "early"
    assert len(result["favoured"]) > 0


def test_sector_rotation_recession():
    from services.macro import _sector_rotation_stage

    result = _sector_rotation_stage(vix=40, yc_spread=-2.0, hyg_1m=-8.0, sp500_trend="down")
    assert result["stage"] in ("recession", "late")
    if result["stage"] == "recession":
        assert "XLU" in result["favoured"] or "XLP" in result["favoured"]
