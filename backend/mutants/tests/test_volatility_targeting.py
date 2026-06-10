"""Tests for services/volatility_targeting.py."""

from unittest.mock import AsyncMock, patch

import numpy as np
import pandas as pd
import pytest


def _fake_returns_df(tickers, n_rows=65, seed=42):
    rng = np.random.default_rng(seed)
    data = {}
    for t in tickers:
        returns = rng.normal(0.0005, 0.015, n_rows)
        data[t] = pd.Series(returns)
    return pd.DataFrame(data).dropna()


def _fake_histories(tickers, n_rows=65):
    result = {}
    rng = np.random.default_rng(7)
    for t in tickers:
        closes = np.abs(100 + rng.normal(0, 1, n_rows + 1).cumsum()) + 50
        df = pd.DataFrame({"Close": closes})
        result[t] = df
    return result


class TestVolTargetWeights:
    def test_empty_df_returns_empty(self):
        from services.volatility_targeting import _vol_target_weights

        result = _vol_target_weights(pd.DataFrame())
        assert result == {}

    def test_single_ticker_returns_result(self):
        from services.volatility_targeting import _vol_target_weights

        df = _fake_returns_df(["SPY"])
        result = _vol_target_weights(df)
        assert "assets" in result
        assert len(result["assets"]) == 1
        assert result["assets"][0]["ticker"] == "SPY"

    def test_multiple_tickers_weights_sum_to_one(self):
        from services.volatility_targeting import _vol_target_weights

        df = _fake_returns_df(["SPY", "QQQ", "IWM", "GLD"])
        result = _vol_target_weights(df)
        total = sum(a["weight_pct"] for a in result["assets"])
        assert abs(total - 100.0) < 1.0  # rounding tolerance

    def test_high_corr_pairs_detected(self):
        from services.volatility_targeting import _vol_target_weights

        # Build two very correlated series
        base = np.random.default_rng(0).normal(0, 0.01, 65)
        df = pd.DataFrame({"A": base, "B": base * 0.99 + np.random.default_rng(1).normal(0, 0.0001, 65)})
        result = _vol_target_weights(df)
        assert len(result.get("high_correlation_pairs", [])) > 0

    def test_scale_factor_capped_at_2(self):
        from services.volatility_targeting import _vol_target_weights

        # Very low vol series → scale_factor would be huge without cap
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"X": rng.normal(0, 0.0001, 65), "Y": rng.normal(0, 0.0001, 65)})
        result = _vol_target_weights(df)
        assert result["scale_factor"] <= 2.0

    def test_zero_vol_ticker_handled(self):
        from services.volatility_targeting import _vol_target_weights

        df = pd.DataFrame({"FLAT": np.zeros(65), "SPY": np.random.default_rng(0).normal(0, 0.01, 65)})
        result = _vol_target_weights(df)
        assert "assets" in result


class TestGetVolatilityTargetWeights:
    @pytest.mark.asyncio
    async def test_uses_default_tickers_when_none_provided(self):
        from services.volatility_targeting import get_volatility_target_weights

        df = _fake_returns_df(["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"])

        with patch("services.volatility_targeting._fetch_returns", AsyncMock(return_value=df)):
            result = await get_volatility_target_weights()

        assert "assets" in result

    @pytest.mark.asyncio
    async def test_too_few_tickers_returns_error(self):
        from services.volatility_targeting import get_volatility_target_weights

        result = await get_volatility_target_weights(["SPY"])
        assert "error" in result

    @pytest.mark.asyncio
    async def test_empty_returns_df_returns_error(self):
        from services.volatility_targeting import get_volatility_target_weights

        with patch("services.volatility_targeting._fetch_returns", AsyncMock(return_value=pd.DataFrame())):
            result = await get_volatility_target_weights(["SPY", "QQQ"])

        assert "error" in result

    @pytest.mark.asyncio
    async def test_exception_returns_error_dict(self):
        from services.volatility_targeting import get_volatility_target_weights

        with patch("services.volatility_targeting._fetch_returns", AsyncMock(side_effect=RuntimeError("boom"))):
            result = await get_volatility_target_weights(["SPY", "QQQ"])

        assert "error" in result

    @pytest.mark.asyncio
    async def test_tickers_uppercased(self):
        from services.volatility_targeting import get_volatility_target_weights

        df = _fake_returns_df(["SPY", "QQQ"])

        with patch("services.volatility_targeting._fetch_returns", AsyncMock(return_value=df)) as mock_fetch:
            await get_volatility_target_weights(["spy", " qqq "])
            called_tickers = mock_fetch.call_args[0][0]

        assert all(t == t.upper() for t in called_tickers)

    @pytest.mark.asyncio
    async def test_result_includes_tickers_metadata(self):
        from services.volatility_targeting import get_volatility_target_weights

        df = _fake_returns_df(["SPY", "QQQ", "GLD"])

        with patch("services.volatility_targeting._fetch_returns", AsyncMock(return_value=df)):
            result = await get_volatility_target_weights(["SPY", "QQQ", "GLD"])

        assert "tickers_requested" in result
        assert "tickers_resolved" in result


class TestFetchReturns:
    @pytest.mark.asyncio
    async def test_empty_histories_returns_empty_df(self):
        from services.volatility_targeting import _fetch_returns

        with patch("services.market_data.get_histories_batch", AsyncMock(return_value={})):
            result = await _fetch_returns(["SPY"])

        assert result.empty

    @pytest.mark.asyncio
    async def test_ticker_with_too_few_rows_skipped(self):
        from services.volatility_targeting import _fetch_returns

        histories = {"SPY": pd.DataFrame({"Close": [100.0, 101.0, 99.0]})}
        with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
            result = await _fetch_returns(["SPY"])

        assert result.empty

    @pytest.mark.asyncio
    async def test_valid_histories_returns_returns_df(self):
        from services.volatility_targeting import _fetch_returns

        histories = _fake_histories(["SPY", "QQQ"])
        with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
            result = await _fetch_returns(["SPY", "QQQ"])

        assert not result.empty
        assert "SPY" in result.columns
        assert "QQQ" in result.columns
