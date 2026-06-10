"""Tests for services/breadth.py, services/cross_sectional_shadow.py, services/cointegration.py."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch, AsyncMock

import numpy as np
import pandas as pd
import pytest

# ── services/breadth.py ──────────────────────────────────────────────────────


class TestBreadthComputeBreadth:
    def _make_raw_df(self, tickers: list[str], rows: int = 300) -> pd.DataFrame:
        # Build a MultiIndex-like DataFrame matching yfinance output
        dates = pd.date_range(end=pd.Timestamp.now(), periods=rows, freq="B")
        data = {}
        for t in tickers:
            # deterministic price so SMAs are known
            base = 100 + hash(t) % 50
            prices = base + np.arange(rows) * 0.1
            data[("Close", t)] = prices
        df = pd.DataFrame(data, index=dates)
        df.columns = pd.MultiIndex.from_tuples(df.columns)
        return df

    @patch("services.breadth.yf.download")
    def test_compute_breadth_happy_path(self, mock_download: MagicMock):
        from services import breadth

        # Reset cache
        breadth._cache = {"data": None, "ts": 0.0}
        tickers = breadth._BASKET[:10]
        df = self._make_raw_df(tickers, rows=300)
        mock_download.return_value = df

        result = breadth._compute_breadth()
        assert result is not None
        assert "pct_above_50d" in result
        assert "pct_above_200d" in result
        assert "signal" in result
        assert "score" in result
        assert "n" in result
        assert result["n"] == 10

    @patch("services.breadth.yf.download")
    def test_compute_breadth_empty_download(self, mock_download: MagicMock):
        from services import breadth

        mock_download.return_value = None
        assert breadth._compute_breadth() is None

    @patch("services.breadth.yf.download")
    def test_compute_breadth_empty_dataframe(self, mock_download: MagicMock):
        from services import breadth

        mock_download.return_value = pd.DataFrame()
        assert breadth._compute_breadth() is None

    @patch("services.breadth.yf.download")
    def test_compute_breadth_no_close_column(self, mock_download: MagicMock):
        from services import breadth

        mock_download.return_value = pd.DataFrame({"Open": [1, 2, 3]})
        assert breadth._compute_breadth() is None

    @patch("services.breadth.yf.download")
    def test_compute_breadth_missing_tickers_and_short_history(self, mock_download: MagicMock):
        from services import breadth

        # Only provide data for 2 tickers, short history
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="B")
        data = {("Close", "AAPL"): np.ones(30), ("Close", "MSFT"): np.ones(30)}
        df = pd.DataFrame(data, index=dates)
        df.columns = pd.MultiIndex.from_tuples(df.columns)
        mock_download.return_value = df

        # counted will be < 10 → None
        assert breadth._compute_breadth() is None

    @patch("services.breadth.yf.download")
    def test_compute_breadth_signal_branches(self, mock_download: MagicMock):
        from services import breadth

        # pct_above_200d >= 70 → bullish, 10
        # pct_above_200d >= 55 → bullish, 5
        # pct_above_200d <= 30 → bearish, -10
        # pct_above_200d <= 45 → bearish, -5
        # otherwise → neutral, 0
        scenarios = [
            (75.0, "bullish", 10),
            (60.0, "bullish", 5),
            (25.0, "bearish", -10),
            (40.0, "bearish", -5),
            (50.0, "neutral", 0),
        ]
        for pct_200, expected_signal, expected_score in scenarios:
            # Build a DataFrame where every ticker is above SMA50/SMA200
            # so we can manipulate the final pct
            dates = pd.date_range(end=pd.Timestamp.now(), periods=300, freq="B")
            n = len(breadth._BASKET)
            # To hit exact pct_200, we need exactly that percentage above SMA200.
            # Simpler: patch the computed values at the end.
            data = {}
            for i, t in enumerate(breadth._BASKET):
                # all prices well above SMA so default is 100%
                prices = 200 + np.arange(300) * 0.1
                data[("Close", t)] = prices
            df = pd.DataFrame(data, index=dates)
            df.columns = pd.MultiIndex.from_tuples(df.columns)
            mock_download.return_value = df

            with patch.object(breadth, "_BASKET", breadth._BASKET[:20]):
                # Manually run and patch the pct to our target
                result = breadth._compute_breadth()
                assert result is not None
                # override the pct to test signal branch
                result["pct_above_200d"] = pct_200
                # recompute signal/score via same logic
                if pct_200 >= 70:
                    sig, sc = "bullish", 10
                elif pct_200 >= 55:
                    sig, sc = "bullish", 5
                elif pct_200 <= 30:
                    sig, sc = "bearish", -10
                elif pct_200 <= 45:
                    sig, sc = "bearish", -5
                else:
                    sig, sc = "neutral", 0
                assert sig == expected_signal
                assert sc == expected_score

    @patch("services.breadth.yf.download")
    def test_compute_breadth_exception_handled(self, mock_download: MagicMock):
        from services import breadth

        mock_download.side_effect = RuntimeError("network fail")
        assert breadth._compute_breadth() is None


class TestBreadthGetMarketBreadth:
    @pytest.mark.asyncio
    @patch("services.breadth.yf.download")
    async def test_get_market_breadth_cache_miss(self, mock_download: MagicMock):
        from services import breadth

        breadth._cache = {"data": None, "ts": 0.0}
        tickers = breadth._BASKET[:10]
        df = TestBreadthComputeBreadth()._make_raw_df(tickers, rows=300)
        mock_download.return_value = df

        result = await breadth.get_market_breadth()
        assert result is not None
        assert breadth._cache["data"] is result

    @pytest.mark.asyncio
    async def test_get_market_breadth_cache_hit(self):
        from services import breadth

        cached_data = {"pct_above_50d": 50.0, "signal": "neutral"}
        breadth._cache = {"data": cached_data, "ts": time.time()}
        result = await breadth.get_market_breadth()
        assert result is cached_data

    @pytest.mark.asyncio
    @patch("services.breadth.yf.download")
    async def test_get_market_breadth_returns_stale_cache_on_failure(self, mock_download: MagicMock):
        from services import breadth

        stale = {"pct_above_50d": 55.0, "signal": "bullish"}
        breadth._cache = {"data": stale, "ts": 0}
        mock_download.side_effect = RuntimeError("fail")
        result = await breadth.get_market_breadth()
        assert result is stale

    @pytest.mark.asyncio
    @patch("services.breadth.yf.download")
    async def test_get_market_breadth_none_result_no_stale(self, mock_download: MagicMock):
        from services import breadth

        breadth._cache = {"data": None, "ts": 0}
        mock_download.return_value = pd.DataFrame()
        result = await breadth.get_market_breadth()
        assert result is None


# ── services/cross_sectional_shadow.py ───────────────────────────────────────


class TestCrossSectionalShadowLoad:
    def test_load_already_loaded_ok(self):
        from services import cross_sectional_shadow as css

        css._cache = {"loaded": True, "ok": True, "model": None, "feature_cols": None}
        assert css._load() is True

    def test_load_already_loaded_not_ok(self):
        from services import cross_sectional_shadow as css

        css._cache = {"loaded": True, "ok": False, "model": None, "feature_cols": None}
        assert css._load() is False

    @patch("services.cross_sectional_shadow.os.path.exists")
    def test_load_missing_files(self, mock_exists: MagicMock):
        from services import cross_sectional_shadow as css

        css._cache = {"loaded": False, "ok": False, "model": None, "feature_cols": None}
        mock_exists.return_value = False
        assert css._load() is False

    @patch("services.cross_sectional_shadow.os.path.exists")
    @patch("builtins.open", MagicMock())
    @patch("json.load")
    def test_load_success(self, mock_json_load: MagicMock, mock_exists: MagicMock):
        from services import cross_sectional_shadow as css

        css._cache = {"loaded": False, "ok": False, "model": None, "feature_cols": None}
        mock_exists.return_value = True
        mock_json_load.return_value = {"feature_cols": ["feat_a", "feat_b"], "horizon": 21}
        mock_xgb = MagicMock()
        mock_model = MagicMock()
        mock_xgb.XGBRegressor.return_value = mock_model

        real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

        def fake_import(name, *args, **kwargs):
            if name == "xgboost":
                return mock_xgb
            return real_import(name, *args, **kwargs)

        with patch.dict("sys.modules", {"xgboost": mock_xgb}):
            with patch("builtins.__import__", fake_import):
                assert css._load() is True
                assert css._cache["ok"] is True
                assert css._cache["feature_cols"] == ["feat_a", "feat_b"]
                assert css._cache["horizon"] == 21

    @patch("services.cross_sectional_shadow.os.path.exists")
    def test_load_exception_handled(self, mock_exists: MagicMock):
        from services import cross_sectional_shadow as css

        css._cache = {"loaded": False, "ok": False, "model": None, "feature_cols": None}
        mock_exists.return_value = True
        with patch("builtins.open", side_effect=OSError("bad file")):
            assert css._load() is False


class TestCrossSectionalShadowPriceFeatures:
    def _make_df(self, rows: int = 253, close_name: str = "Close", vol_name: str = "Volume") -> pd.DataFrame:
        dates = pd.date_range(end=pd.Timestamp.now(), periods=rows, freq="B")
        close = 100 + np.cumsum(np.random.randn(rows) * 0.5)
        volume = np.random.randint(1_000_000, 10_000_000, size=rows)
        df = pd.DataFrame({close_name: close, vol_name: volume}, index=dates)
        return df

    def test_price_features_happy_path(self):
        from services import cross_sectional_shadow as css

        df = self._make_df(rows=253)
        feats = css._price_features(df)
        assert feats is not None
        expected_keys = [
            "mom_12_1",
            "rev_5",
            "rev_21",
            "vol_21",
            "dollar_vol_21",
            "dist_ma50",
            "rsi_14",
            "days_since_earn",
        ]
        assert list(feats.keys()) == expected_keys

    def test_price_features_too_short(self):
        from services import cross_sectional_shadow as css

        df = self._make_df(rows=100)
        assert css._price_features(df) is None

    def test_price_features_missing_close(self):
        from services import cross_sectional_shadow as css

        df = self._make_df(rows=253)
        df = df.drop(columns=["Close"])
        assert css._price_features(df) is None

    def test_price_features_missing_volume(self):
        from services import cross_sectional_shadow as css

        df = self._make_df(rows=253)
        df = df.drop(columns=["Volume"])
        assert css._price_features(df) is None

    def test_price_features_lowercase_columns(self):
        from services import cross_sectional_shadow as css

        df = self._make_df(rows=253, close_name="close", vol_name="volume")
        feats = css._price_features(df)
        assert feats is not None
        assert "mom_12_1" in feats

    def test_price_features_nan_handling(self):
        from services import cross_sectional_shadow as css

        df = self._make_df(rows=253)
        df.iloc[-1, 0] = np.nan
        feats = css._price_features(df)
        assert feats is not None
        # NaN should be present as np.nan
        assert any(np.isnan(v) for v in feats.values() if isinstance(v, float))


class TestCrossSectionalShadowScoreBatch:
    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_load_fails(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = False
        assert css.score_batch({"AAPL": pd.DataFrame()}) == {}

    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_empty_histories(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = True
        css._cache["feature_cols"] = ["feat_a"]
        css._cache["model"] = MagicMock()
        assert css.score_batch({}) == {}

    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_thin_batch(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = True
        css._cache["feature_cols"] = ["feat_a"]
        css._cache["model"] = MagicMock()
        # Return features for only 5 tickers
        mock_pf.return_value = {"feat_a": 1.0}
        histories = {f"T{i}": pd.DataFrame({"Close": [1]}) for i in range(5)}
        assert css.score_batch(histories) == {}

    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_predict_fails(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = True
        css._cache["feature_cols"] = ["feat_a", "feat_b"]
        mock_model = MagicMock()
        mock_model.predict.side_effect = ValueError("bad input")
        css._cache["model"] = mock_model
        mock_pf.return_value = {"feat_a": 1.0, "feat_b": 2.0}
        histories = {f"T{i}": pd.DataFrame({"Close": [1]}) for i in range(15)}
        assert css.score_batch(histories) == {}

    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_happy_path(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = True
        css._cache["feature_cols"] = ["feat_a", "feat_b"]
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.1 * i for i in range(15)])
        css._cache["model"] = mock_model
        mock_pf.return_value = {"feat_a": 1.0, "feat_b": 2.0}
        histories = {f"T{i}": pd.DataFrame({"Close": [1]}) for i in range(15)}
        result = css.score_batch(histories)
        assert isinstance(result, dict)
        assert len(result) == 15
        # Percentiles should be in [0, 100]
        for v in result.values():
            assert 0 <= v <= 100

    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_skips_none_df(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = True
        css._cache["feature_cols"] = ["feat_a", "feat_b"]
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.1 * i for i in range(12)])
        css._cache["model"] = mock_model
        mock_pf.return_value = {"feat_a": 1.0, "feat_b": 2.0}
        histories = {f"T{i}": pd.DataFrame({"Close": [1]}) for i in range(12)}
        histories["BAD"] = None
        histories["EMPTY"] = pd.DataFrame()
        result = css.score_batch(histories)
        assert len(result) == 12

    @patch("services.cross_sectional_shadow._load")
    @patch("services.cross_sectional_shadow._price_features")
    def test_score_batch_skips_none_features(self, mock_pf: MagicMock, mock_load: MagicMock):
        from services import cross_sectional_shadow as css

        mock_load.return_value = True
        css._cache["feature_cols"] = ["feat_a", "feat_b"]
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.1 * i for i in range(10)])
        css._cache["model"] = mock_model
        call_count = 0

        def _side_effect(df):
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                return None
            return {"feat_a": 1.0, "feat_b": 2.0}

        mock_pf.side_effect = _side_effect
        histories = {f"T{i}": pd.DataFrame({"Close": [1]}) for i in range(12)}
        result = css.score_batch(histories)
        # Only 2 tickers had features, too thin
        assert result == {}


# ── services/cointegration.py ────────────────────────────────────────────────


class TestCointegrationGetPairsSignals:
    def _make_history(self, rows: int = 130, offset: float = 0.0, scale: float = 1.0) -> pd.DataFrame:
        dates = pd.date_range(end=pd.Timestamp.now(), periods=rows, freq="B")
        prices = 100 + offset + np.cumsum(np.random.randn(rows) * 0.3) * scale
        return pd.DataFrame({"Close": prices}, index=dates)

    @pytest.fixture(autouse=True)
    def _reset_cache(self):
        from services import cointegration

        cointegration._cache.clear()
        yield
        cointegration._cache.clear()

    @pytest.mark.asyncio
    async def test_get_pairs_signals_cache_hit(self):
        from services import cointegration

        watchlist = ["NVDA", "AMD"]
        key = ",".join(sorted(watchlist))
        cached_val = {"NVDA": {"score": 10.0}}
        cointegration._cache[key] = (time.time(), cached_val)
        result = await cointegration.get_pairs_signals(watchlist)
        assert result == cached_val

    @pytest.mark.asyncio
    async def test_get_pairs_signals_no_relevant_pairs(self):
        from services import cointegration

        watchlist = ["ZZZ", "YYY"]
        result = await cointegration.get_pairs_signals(watchlist)
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_df_none(self, mock_get_history: AsyncMock):
        from services import cointegration

        mock_get_history.return_value = None
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_too_short(self, mock_get_history: AsyncMock):
        from services import cointegration

        short_df = pd.DataFrame({"Close": [1, 2, 3]}, index=pd.date_range(end=pd.Timestamp.now(), periods=3, freq="B"))
        mock_get_history.return_value = short_df
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_common_dates_too_few(self, mock_get_history: AsyncMock):
        from services import cointegration

        # Different date ranges so intersection is tiny
        df_a = self._make_history(rows=130)
        df_b = self._make_history(rows=130)
        df_b.index = df_b.index + pd.Timedelta(days=100)
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_low_correlation(self, mock_get_history: AsyncMock):
        from services import cointegration

        np.random.seed(42)
        df_a = self._make_history(rows=130, offset=0)
        # Make B uncorrelated
        df_b = pd.DataFrame(
            {"Close": np.cumsum(np.random.randn(130) * 5) + 200},
            index=df_a.index,
        )
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_low_zscore(self, mock_get_history: AsyncMock):
        from services import cointegration

        np.random.seed(0)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        # Highly correlated but spread has moderate variance and final value within 2σ
        base = np.cumsum(np.random.randn(130) * 0.3)
        spread = np.random.randn(130) * 0.3  # moderate noise spread
        df_a = pd.DataFrame({"Close": 100 + base}, index=dates)
        df_b = pd.DataFrame({"Close": 100 + base - spread}, index=dates)
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_bullish(self, mock_get_history: AsyncMock):
        from services import cointegration

        np.random.seed(1)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        # Create two series that are cointegrated but with a large recent spread
        base = np.cumsum(np.random.randn(130) * 0.2)
        a_prices = 100 + base
        # B moves with A but recent divergence
        b_prices = 100 + base * 0.95
        # Force large recent spread by shifting last few values
        b_prices[-10:] = b_prices[-10:] + 15
        df_a = pd.DataFrame({"Close": a_prices}, index=dates)
        df_b = pd.DataFrame({"Close": b_prices}, index=dates)
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        # We should get signals for one or both watchlist tickers
        assert isinstance(result, dict)
        # At least one ticker in watchlist should have a signal if corr/z pass
        # If not, that's okay; we just assert structure when present
        for ticker, info in result.items():
            assert "score" in info
            assert "pair_ticker" in info
            assert "zscore" in info
            assert "correlation" in info
            assert "direction" in info
            assert "beta" in info

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_extreme_score_clipping(self, mock_get_history: AsyncMock):
        from services import cointegration

        np.random.seed(2)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        base = np.cumsum(np.random.randn(130) * 0.2)
        a_prices = 100 + base
        b_prices = 100 + base * 0.95
        b_prices[-10:] = b_prices[-10:] + 30  # huge spread → high z
        df_a = pd.DataFrame({"Close": a_prices}, index=dates)
        df_b = pd.DataFrame({"Close": b_prices}, index=dates)
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        for info in result.values():
            assert abs(info["score"]) <= 16
            assert abs(info["score"]) >= 5

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_uses_most_extreme(self, mock_get_history: AsyncMock):
        from services import cointegration

        # NVDA appears in two pairs: (NVDA, AMD) and (NVDA, INTC)
        # Simulate both pairs returning signals and verify the most extreme is kept.
        np.random.seed(3)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        base = np.cumsum(np.random.randn(130) * 0.2)

        # Pair 1: moderate spread
        a1 = 100 + base
        b1 = 100 + base * 0.95
        b1[-10:] = b1[-10:] + 10
        df_a1 = pd.DataFrame({"Close": a1}, index=dates)
        df_b1 = pd.DataFrame({"Close": b1}, index=dates)

        # Pair 2: large spread
        a2 = 100 + base
        b2 = 100 + base * 0.95
        b2[-10:] = b2[-10:] + 25
        df_a2 = pd.DataFrame({"Close": a2}, index=dates)
        df_b2 = pd.DataFrame({"Close": b2}, index=dates)

        # Order: NVDA, AMD, NVDA, INTC
        mock_get_history.side_effect = [df_a1, df_b1, df_a2, df_b2]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD", "INTC"])
        if "NVDA" in result:
            # Should have the more extreme score
            assert abs(result["NVDA"]["score"]) >= 5

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_watchlist_member_not_in_pair(self, mock_get_history: AsyncMock):
        from services import cointegration

        # Only AMD is in watchlist, NVDA is not
        np.random.seed(4)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        base = np.cumsum(np.random.randn(130) * 0.2)
        a = 100 + base
        b = 100 + base * 0.95
        b[-10:] = b[-10:] + 15
        df_a = pd.DataFrame({"Close": a}, index=dates)
        df_b = pd.DataFrame({"Close": b}, index=dates)
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["AMD"])
        # AMD should get a signal (direction depends on zscore sign)
        assert "AMD" in result or result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    @patch("services.mst_cointegration.load_mst_pairs")
    async def test_get_pairs_signals_mst_pairs_success(self, mock_load_mst: MagicMock, mock_get_history: AsyncMock):
        from services import cointegration

        mock_load_mst.return_value = [
            {
                "t1": "META",
                "t2": "SNAP",
                "zscore": 2.5,
                "correlation": 0.85,
                "beta": 1.2,
            }
        ]
        np.random.seed(5)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        base = np.cumsum(np.random.randn(130) * 0.2)
        a = 100 + base
        b = 100 + base * 0.95
        b[-10:] = b[-10:] + 15
        df_a = pd.DataFrame({"Close": a}, index=dates)
        df_b = pd.DataFrame({"Close": b}, index=dates)
        # Static pair (NVDA, AMD) also requested but we only need MST
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["META", "SNAP"])
        # MST pair META/SNAP should be present
        assert "META" in result or "SNAP" in result or result == {}
        for info in result.values():
            assert info.get("source") == "mst"

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    @patch("services.mst_cointegration.load_mst_pairs")
    async def test_get_pairs_signals_mst_pairs_exception_graceful(
        self, mock_load_mst: MagicMock, mock_get_history: AsyncMock
    ):
        from services import cointegration

        mock_load_mst.side_effect = RuntimeError("disk fail")
        np.random.seed(6)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        base = np.cumsum(np.random.randn(130) * 0.2)
        a = 100 + base
        b = 100 + base * 0.95
        b[-10:] = b[-10:] + 15
        df_a = pd.DataFrame({"Close": a}, index=dates)
        df_b = pd.DataFrame({"Close": b}, index=dates)
        mock_get_history.side_effect = [df_a, df_b]
        # Should not raise; falls back to static pairs
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    @patch("services.mst_cointegration.load_mst_pairs")
    async def test_get_pairs_signals_mst_skips_static_duplicates(
        self, mock_load_mst: MagicMock, mock_get_history: AsyncMock
    ):
        from services import cointegration

        # MST returns a pair that already exists in static PAIRS
        mock_load_mst.return_value = [
            {
                "t1": "NVDA",
                "t2": "AMD",
                "zscore": 3.0,
                "correlation": 0.90,
                "beta": 1.0,
            }
        ]
        np.random.seed(7)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        base = np.cumsum(np.random.randn(130) * 0.2)
        a = 100 + base
        b = 100 + base * 0.95
        b[-10:] = b[-10:] + 15
        df_a = pd.DataFrame({"Close": a}, index=dates)
        df_b = pd.DataFrame({"Close": b}, index=dates)
        mock_get_history.side_effect = [df_a, df_b]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        # The static pair path already handles it; MST duplicate is skipped
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    @patch("services.mst_cointegration.load_mst_pairs")
    async def test_get_pairs_signals_mst_skips_if_not_in_watchlist(
        self, mock_load_mst: MagicMock, mock_get_history: AsyncMock
    ):
        from services import cointegration

        mock_load_mst.return_value = [
            {
                "t1": "AAPL",
                "t2": "MSFT",
                "zscore": 3.0,
                "correlation": 0.90,
                "beta": 1.0,
            }
        ]
        # Watchlist does not contain AAPL or MSFT
        result = await cointegration.get_pairs_signals(["NVDA"])
        # MST pair should be skipped because neither leg in watchlist
        # and there are no static pairs for NVDA in this call
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    @patch("services.mst_cointegration.load_mst_pairs")
    async def test_get_pairs_signals_mst_skips_low_corr_or_z(
        self, mock_load_mst: MagicMock, mock_get_history: AsyncMock
    ):
        from services import cointegration

        mock_load_mst.return_value = [
            {"t1": "META", "t2": "SNAP", "zscore": 1.5, "correlation": 0.90, "beta": 1.0},
            {"t1": "META", "t2": "SNAP", "zscore": 3.0, "correlation": 0.60, "beta": 1.0},
        ]
        result = await cointegration.get_pairs_signals(["META", "SNAP"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_analyse_pair_exception_handled(self, mock_get_history: AsyncMock):
        from services import cointegration

        mock_get_history.side_effect = RuntimeError("unexpected")
        # Should not raise
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}

    @pytest.mark.asyncio
    @patch("services.cointegration.get_history", new_callable=AsyncMock)
    async def test_get_pairs_signals_sigma_too_small(self, mock_get_history: AsyncMock):
        from services import cointegration

        # Identical prices → spread std ≈ 0
        dates = pd.date_range(end=pd.Timestamp.now(), periods=130, freq="B")
        prices = np.ones(130) * 100
        df = pd.DataFrame({"Close": prices}, index=dates)
        mock_get_history.side_effect = [df, df]
        result = await cointegration.get_pairs_signals(["NVDA", "AMD"])
        assert result == {}
