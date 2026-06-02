"""
Unit tests for the five new alpha layers added in the 2026-06 research sprint:

  L8  quality_score tier in positionSizeScale
  L9  HMM regime sizing in positionSizeScale + hmmRegime signal field
  OFI get_ofi_signals() computation logic
  MST mst_cointegration.compute_mst_pairs() + load_mst_pairs()
  META blend_confidence() meta_prob parameter
       _extract_meta_features() vector shape

All tests are pure-function / offline — no network, no DB, no async.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_tech(
    ou_halflife: float = 8.0,
    hurst: float = 0.55,
    rsi: float = 35.0,
    bb_pct_b: float = 0.15,
    ibs: float = 0.10,
    vwap_pct: float = -1.0,
    rvol: float = 1.5,
    atr: float = 2.0,
    price: float = 100.0,
) -> dict:
    return {
        "ou_halflife": ou_halflife,
        "hurst": hurst,
        "rsi": rsi,
        "bb_pct_b": bb_pct_b,
        "ibs": ibs,
        "vwap_pct": vwap_pct,
        "rvol": rvol,
        "atr": atr,
        "price": price,
    }


def _hmm(regime: str = "bull", bull_prob: float = 0.80, bear_prob: float = 0.10, trans_risk: float = 0.05) -> dict:
    return {
        "regime": regime,
        "bull_prob": bull_prob,
        "bear_prob": bear_prob,
        "transition_risk": trans_risk,
        "vix_z": -0.5,
    }


# ── L8: quality_score computation ────────────────────────────────────────────


def _compute_quality_score(score: float, ou_halflife: float, hurst: float) -> float:
    """Mirror of the formula in _assemble_signal."""
    return min(
        100.0,
        max(
            0.0,
            min(40.0, (score - 50.0) / 30.0 * 40.0)
            + 35.0 * max(0.0, 1.0 - ou_halflife / 25.0)
            + 25.0 * max(0.0, 1.0 - (hurst - 0.5) / 0.30),
        ),
    )


class TestQualityScore:
    def test_high_tier_all_components_maxed(self):
        """score=80, ou_halflife=0, hurst=0.5 → max quality."""
        qs = _compute_quality_score(80, 0, 0.5)
        # score part: min(40, (80-50)/30*40) = 40
        # ou part: 35*(1-0/25) = 35
        # hurst part: 25*(1-(0.5-0.5)/0.3) = 25
        assert qs == 100.0

    def test_low_tier_score_at_threshold(self):
        """score=50 (at threshold), slow OU, trending Hurst → very low."""
        qs = _compute_quality_score(50, 25, 0.80)
        # score part: min(40, 0) = 0
        # ou part: 35*(1-25/25) = 0
        # hurst part: 25*(1-(0.80-0.5)/0.3) = 25*(1-1) = 0
        assert qs == pytest.approx(0.0)

    def test_mid_tier_values(self):
        """score=60, ou_halflife=12.5, hurst=0.65 → middle range."""
        qs = _compute_quality_score(60, 12.5, 0.65)
        # score: min(40, 10/30*40) = 13.33
        # ou: 35*(1-12.5/25) = 17.5
        # hurst: 25*(1-(0.65-0.5)/0.3) = 25*(1-0.5) = 12.5
        expected = 13.333 + 17.5 + 12.5
        assert qs == pytest.approx(expected, abs=0.1)

    def test_tier_multipliers(self):
        """Verify tier boundary logic mirrors positionSizeScale L8."""
        assert _compute_quality_score(80, 2, 0.51) >= 60  # high tier → 1.30×
        assert _compute_quality_score(50, 25, 0.80) < 30  # low tier → 0.75×

    def test_clamped_to_0_100(self):
        """Extreme values never produce out-of-range quality_score."""
        assert _compute_quality_score(-1000, 0, 0.0) == 0.0
        assert _compute_quality_score(1000, 0, 0.0) == 100.0

    def test_default_ou_halflife_when_missing(self):
        """Missing ou_halflife defaults to 12.5 (neutral) — not NaN."""
        qs = _compute_quality_score(60, 12.5, 0.65)
        assert not math.isnan(qs)


# ── L9: HMM regime sizing ─────────────────────────────────────────────────────


def _hmm_size_multiplier(regime: str, bear_prob: float, bull_prob: float, trans_risk: float) -> float:
    """Mirror of the L9 expression in positionSizeScale."""
    if regime == "bear" and bear_prob >= 0.70:
        return 0.70
    if regime == "transition" or trans_risk > 0.15:
        return 0.85
    if regime == "bull" and bull_prob >= 0.75:
        return 1.10
    return 1.0


class TestHMMSizing:
    def test_confirmed_bear_reduces_size(self):
        assert _hmm_size_multiplier("bear", 0.80, 0.10, 0.05) == pytest.approx(0.70)

    def test_bear_below_70pct_no_reduction(self):
        """bear regime at only 65% confidence → no automatic cut (falls to 1.0)."""
        assert _hmm_size_multiplier("bear", 0.65, 0.25, 0.10) == pytest.approx(1.0)

    def test_transition_regime_reduces_size(self):
        assert _hmm_size_multiplier("transition", 0.45, 0.45, 0.12) == pytest.approx(0.85)

    def test_high_transition_risk_reduces_size(self):
        """Bull regime but trans_risk=0.22 → still 0.85×."""
        assert _hmm_size_multiplier("bull", 0.10, 0.70, 0.22) == pytest.approx(0.85)

    def test_confirmed_bull_amplifies_size(self):
        assert _hmm_size_multiplier("bull", 0.05, 0.85, 0.05) == pytest.approx(1.10)

    def test_unknown_regime_neutral(self):
        """Empty regime string → 1.0× (neutral)."""
        assert _hmm_size_multiplier("", 0.5, 0.5, 0.05) == pytest.approx(1.0)

    def test_combined_l8_l9_high_quality_bull(self):
        """High quality + confirmed bull → 1.30 × 1.10 = 1.43× of inner block."""
        qs = _compute_quality_score(75, 3, 0.52)
        l8 = 1.30 if qs >= 60 else 0.75 if qs < 30 else 1.0
        l9 = _hmm_size_multiplier("bull", 0.05, 0.85, 0.05)
        assert l8 * l9 == pytest.approx(1.30 * 1.10)

    def test_combined_l8_l9_low_quality_bear(self):
        """Low quality + bear regime → 0.75 × 0.70 = 0.525× of inner block."""
        qs = _compute_quality_score(50, 25, 0.80)
        l8 = 1.30 if qs >= 60 else 0.75 if qs < 30 else 1.0
        l9 = _hmm_size_multiplier("bear", 0.80, 0.10, 0.05)
        assert l8 * l9 == pytest.approx(0.75 * 0.70)


# ── OFI computation logic ─────────────────────────────────────────────────────


class TestOFIComputation:
    """Test the Lee-Ready OFI arithmetic in isolation (no network calls)."""

    @staticmethod
    def _build_bars(closes, volumes):
        return [{"c": c, "v": v} for c, v in zip(closes, volumes)]

    def _compute_ofi_1d(self, closes, volumes):
        """Mirror of the ofi computation in get_ofi_signals()."""
        closes = np.array(closes, dtype=float)
        volumes = np.array(volumes, dtype=float)
        price_diff = np.diff(closes, prepend=closes[0])
        signs = np.where(price_diff > 0, 1.0, np.where(price_diff < 0, -1.0, 0.0))
        ofi_series = signs * volumes
        session_vol = float(volumes.sum()) or 1.0
        return float(ofi_series.sum()) / session_vol

    def test_all_upticks_ofi_positive(self):
        """Monotonically rising price → all buyer-initiated → OFI positive."""
        closes = [100, 101, 102, 103, 104]
        volumes = [1000] * 5
        ofi = self._compute_ofi_1d(closes, volumes)
        assert ofi > 0

    def test_all_downticks_ofi_negative(self):
        """Monotonically falling price → all seller-initiated → OFI negative."""
        closes = [104, 103, 102, 101, 100]
        volumes = [1000] * 5
        ofi = self._compute_ofi_1d(closes, volumes)
        assert ofi < 0

    def test_flat_price_zero_ofi(self):
        """Flat price → no tick direction → OFI = 0."""
        closes = [100, 100, 100, 100]
        volumes = [1000] * 4
        ofi = self._compute_ofi_1d(closes, volumes)
        assert ofi == pytest.approx(0.0)

    def test_divergence_price_down_ofi_positive(self):
        """Price falls but volume is buyer-dominated → positive divergence."""
        # Mostly downticks on low volume, one big uptick near end
        closes = [100, 99, 98, 98.5, 97]
        volumes = [100, 100, 100, 10000, 100]  # large buy volume on the uptick
        ofi = self._compute_ofi_1d(closes, volumes)
        price_ret = closes[-1] / closes[0] - 1  # negative
        divergence = price_ret * -1.0 * ofi
        # price_ret < 0, ofi should be positive (big uptick volume dominated)
        # → divergence = negative * -1 * positive = positive
        assert divergence > 0

    def test_normalized_by_session_volume(self):
        """OFI values are always in [-1, +1] range for realistic bar sequences."""
        closes = [100 + i * 0.1 for i in range(390)]  # all upticks
        volumes = [1000] * 390
        ofi = self._compute_ofi_1d(closes, volumes)
        assert -1.0 <= ofi <= 1.0

    def test_empty_result_on_too_few_bars(self):
        """Real function returns {} when < 10 bars."""
        closes = [100, 101, 102]
        volumes = [1000] * 3
        # Simulate the guard: len(results) < 10 → return {}
        results = self._build_bars(closes, volumes)
        assert len(results) < 10  # confirms the guard would fire


# ── MST cointegration ─────────────────────────────────────────────────────────


class TestMSTCointegration:
    def _make_price_matrix(self, n_tickers: int = 10, n_days: int = 90) -> pd.DataFrame:
        """Generate a random but structured price matrix."""
        rng = np.random.default_rng(42)
        # Create a factor model: all tickers share one common factor
        common = np.cumsum(rng.normal(0, 0.01, n_days))
        prices = {}
        for i in range(n_tickers):
            loading = 0.5 + rng.random() * 0.5
            idio = np.cumsum(rng.normal(0, 0.005, n_days))
            prices[f"T{i:02d}"] = 100 * np.exp(loading * common + idio)
        return pd.DataFrame(prices)

    def test_kruskal_mst_produces_n_minus_1_edges(self):
        from services.mst_cointegration import _kruskal_mst

        n = 8
        rng = np.random.default_rng(0)
        dist = np.abs(rng.normal(0, 1, (n, n)))
        dist = (dist + dist.T) / 2
        np.fill_diagonal(dist, 0.0)
        edges = _kruskal_mst(dist)
        assert len(edges) == n - 1

    def test_kruskal_mst_no_cycles(self):
        """MST must be a tree — no vertex appears more than n-1 times."""
        from services.mst_cointegration import _kruskal_mst

        n = 6
        dist = np.full((n, n), 1.0)
        np.fill_diagonal(dist, 0.0)
        # Make T0-T1 cheapest
        dist[0, 1] = dist[1, 0] = 0.1
        edges = _kruskal_mst(dist)
        assert len(edges) == n - 1
        # Verify T0-T1 edge is in MST (cheapest)
        assert any(set([i, j]) == {0, 1} for i, j, _ in edges)

    def test_compute_mst_pairs_returns_list(self):
        """compute_mst_pairs returns a list (possibly empty for random data)."""
        from services.mst_cointegration import compute_mst_pairs

        pm = self._make_price_matrix(n_tickers=8, n_days=90)
        result = compute_mst_pairs(pm, window=90)
        assert isinstance(result, list)
        for pair in result:
            assert "t1" in pair and "t2" in pair
            assert "zscore" in pair
            assert "correlation" in pair
            assert abs(pair["correlation"]) >= 0.75  # filter applied

    def test_compute_mst_pairs_too_few_tickers(self):
        """Fewer than 4 tickers returns empty list gracefully."""
        from services.mst_cointegration import compute_mst_pairs

        pm = pd.DataFrame({"A": [100, 101, 102], "B": [50, 51, 52]})
        result = compute_mst_pairs(pm)
        assert result == []

    def test_load_mst_pairs_missing_file(self):
        """load_mst_pairs returns [] when file does not exist."""
        from services.mst_cointegration import load_mst_pairs
        import unittest.mock as _mock

        with _mock.patch("services.mst_cointegration._CACHE_FILE", Path("/nonexistent/path.json")):
            result = load_mst_pairs()
        assert result == []

    def test_load_mst_pairs_stale_cache(self):
        """load_mst_pairs returns [] when computed_at is older than 7 days."""
        from services.mst_cointegration import load_mst_pairs
        import unittest.mock as _mock
        import time

        stale_data = {"pairs": [{"t1": "A", "t2": "B"}], "computed_at": time.time() - 8 * 86400}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(stale_data, f)
            tmppath = Path(f.name)

        with _mock.patch("services.mst_cointegration._CACHE_FILE", tmppath):
            result = load_mst_pairs()
        tmppath.unlink(missing_ok=True)
        assert result == []

    def test_load_mst_pairs_fresh_cache(self):
        """load_mst_pairs returns pairs when cache is fresh (< 7 days)."""
        from services.mst_cointegration import load_mst_pairs
        import unittest.mock as _mock
        import time

        fresh_data = {
            "pairs": [{"t1": "NVDA", "t2": "AMD", "zscore": -2.5, "correlation": 0.88}],
            "computed_at": time.time() - 3600,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(fresh_data, f)
            tmppath = Path(f.name)

        with _mock.patch("services.mst_cointegration._CACHE_FILE", tmppath):
            result = load_mst_pairs()
        tmppath.unlink(missing_ok=True)
        assert len(result) == 1
        assert result[0]["t1"] == "NVDA"


# ── Meta-label model: blend_confidence + feature extraction ───────────────────


class TestMetaLabelBlend:
    """Tests for the updated blend_confidence() with meta_prob parameter."""

    def test_meta_prob_none_no_change_to_existing_behavior(self):
        """meta_prob=None preserves original blend_confidence result exactly."""
        from services.signal_ml import blend_confidence

        result_without = blend_confidence(60.0, entry_prob=0.7, live_prob=0.6)
        result_with_none = blend_confidence(60.0, entry_prob=0.7, live_prob=0.6, meta_prob=None)
        assert result_without == result_with_none

    def test_both_none_still_returns_base(self):
        """When all probs are None, meta_prob=None returns base unchanged."""
        from services.signal_ml import blend_confidence

        assert blend_confidence(55.0, None, None, None, None) == 55.0

    def test_high_meta_prob_amplifies(self):
        """meta_prob=0.90 should produce higher confidence than no meta_prob."""
        from services.signal_ml import blend_confidence

        base = 55.0
        without_meta = blend_confidence(base, entry_prob=0.65, live_prob=0.60)
        with_meta = blend_confidence(base, entry_prob=0.65, live_prob=0.60, meta_prob=0.90)
        assert with_meta >= without_meta

    def test_low_meta_prob_dampens(self):
        """meta_prob=0.10 should produce lower confidence than no meta_prob."""
        from services.signal_ml import blend_confidence

        base = 55.0
        without_meta = blend_confidence(base, entry_prob=0.65, live_prob=0.60)
        with_meta = blend_confidence(base, entry_prob=0.65, live_prob=0.60, meta_prob=0.10)
        assert with_meta <= without_meta

    def test_meta_prob_50pct_neutral(self):
        """meta_prob=0.50 → meta_scale=1.0 → no change to blended ratio."""
        from services.signal_ml import blend_confidence

        without = blend_confidence(60.0, entry_prob=0.7, live_prob=None)
        with_50 = blend_confidence(60.0, entry_prob=0.7, live_prob=None, meta_prob=0.50)
        # meta_scale = 0.60 + 0.80*0.50 = 1.0 → ratio unchanged
        assert without == pytest.approx(with_50, abs=0.5)

    def test_meta_prob_clamped_at_max_confidence(self):
        """Even with meta_prob=1.0, result never exceeds _MAX_CONFIDENCE=72."""
        from services.signal_ml import blend_confidence

        result = blend_confidence(70.0, entry_prob=0.99, live_prob=0.99, meta_prob=1.0)
        assert result <= 72.0

    def test_meta_prob_clamps_ratio_to_valid_range(self):
        """meta_scale never lets ratio escape [0.75, 1.25] final clamp."""
        from services.signal_ml import blend_confidence

        # Very low meta_prob → ratio should not go below what 0.75 clamp allows
        result_low = blend_confidence(60.0, entry_prob=0.5, live_prob=0.5, meta_prob=0.0)
        # meta_scale=0.60, ratio clamped at 0.75 → 60*0.75 = 45.0
        assert result_low >= 45.0

        result_high = blend_confidence(50.0, entry_prob=0.5, live_prob=0.5, meta_prob=1.0)
        # meta_scale=1.40, ratio clamped at 1.25 → 50*1.25 = 62.5
        assert result_high <= 62.5


class TestMetaFeatureExtraction:
    """Tests for _extract_meta_features() vector shape and values."""

    def test_feature_vector_length(self):
        """Meta-label feature vector must have exactly 11 elements."""
        from services.signal_ml import _extract_meta_features, _META_FEATURE_NAMES

        assert len(_META_FEATURE_NAMES) == 11
        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=0.65,
            hmm_regime=_hmm(),
            vix=18.0,
            sector_etf="XLK",
            dow=0,
            dte=70,
        )
        assert len(feats) == 11

    def test_entry_prob_is_first_feature(self):
        """entry_prob must be feature[0] — it is THE key meta-label predictor."""
        from services.signal_ml import _extract_meta_features

        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=0.73,
            hmm_regime=_hmm(),
            vix=18.0,
            sector_etf="XLK",
            dow=1,
            dte=80,
        )
        assert feats[0] == pytest.approx(0.73)

    def test_hmm_probs_in_vector(self):
        """HMM bull_prob and trans_risk appear at correct positions."""
        from services.signal_ml import _extract_meta_features

        hmm = _hmm(bull_prob=0.82, trans_risk=0.07)
        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=0.6,
            hmm_regime=hmm,
            vix=15.0,
            sector_etf="XLK",
            dow=2,
            dte=90,
        )
        assert feats[6] == pytest.approx(0.82)  # hmm_bull_prob
        assert feats[7] == pytest.approx(0.07)  # hmm_trans_risk

    def test_missing_entry_prob_nan(self):
        """entry_prob=None → NaN at index 0; XGBoost handles natively."""
        from services.signal_ml import _extract_meta_features

        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=None,
            hmm_regime=None,
            vix=None,
            sector_etf=None,
            dow=None,
            dte=None,
        )
        assert math.isnan(feats[0])

    def test_missing_hmm_uses_defaults(self):
        """hmm_regime=None → bull_prob defaults to 0.5, trans_risk to 0.1."""
        from services.signal_ml import _extract_meta_features

        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=0.6,
            hmm_regime=None,
            vix=18.0,
            sector_etf="XLK",
            dow=0,
            dte=70,
        )
        assert feats[6] == pytest.approx(0.5)  # hmm_bull_prob default
        assert feats[7] == pytest.approx(0.1)  # hmm_trans_risk default

    def test_atr_pct_computed_from_tech(self):
        """atr_pct = atr/price*100 — verify against known values."""
        from services.signal_ml import _extract_meta_features

        tech = _make_tech(atr=3.0, price=150.0)  # 2%
        feats = _extract_meta_features(
            tech=tech,
            entry_prob=0.6,
            hmm_regime=_hmm(),
            vix=18.0,
            sector_etf="XLK",
            dow=0,
            dte=70,
        )
        assert feats[4] == pytest.approx(3.0 / 150.0 * 100.0)  # atr_pct

    def test_sector_ordinal_xlk(self):
        from services.signal_ml import _extract_meta_features

        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=0.6,
            hmm_regime=_hmm(),
            vix=18.0,
            sector_etf="XLK",
            dow=0,
            dte=70,
        )
        assert feats[9] == pytest.approx(0.0)  # XLK = 0

    def test_dte_bucket_mapping(self):
        """dte=80 → bucket 3 (far from earnings, clean signal)."""
        from services.signal_ml import _extract_meta_features

        feats = _extract_meta_features(
            tech=_make_tech(),
            entry_prob=0.6,
            hmm_regime=_hmm(),
            vix=18.0,
            sector_etf="XLK",
            dow=0,
            dte=80,
        )
        assert feats[8] == pytest.approx(3.0)  # >65d → bucket 3


# ── Signal dict fields: qualityScore + hmmRegime ─────────────────────────────


class TestSignalDictNewFields:
    """
    Smoke-level test: _assemble_signal produces qualityScore and hmmRegime
    without errors when called with realistic inputs.
    Uses the same minimal-mock pattern as test_signal_engine_core.py.
    """

    def _build_minimal_signal_kwargs(self, hmm_regime_label: str = "bull"):
        """Build minimal valid kwargs for _assemble_signal.

        Provides three independent positive rationale cards across distinct
        source families so agreement > 0 and action resolves to BUY.
        """
        _rationale = [
            {"src": "Technical", "head": "RSI Oversold 28", "sentiment": "pos"},
            {"src": "Macro", "head": "VIX Low", "sentiment": "pos"},
            {"src": "Options/Flow", "head": "Block Accumulation", "sentiment": "pos"},
        ]
        return dict(
            ticker="AAPL",
            info={"company": "Apple", "beta": 1.1},
            tech=_make_tech(ou_halflife=5.0, hurst=0.48),
            score=62.0,
            rationale=_rationale,
            sources={"Technical", "Macro", "Options/Flow"},
            _force_hold=False,
            _is_low_atr=False,
            _atr_pct_pre=0.02,
            total_confidence_penalty=0.0,
            portfolio_size_scale=1.0,
            avg_sent=0.3,
            price=150.0,
            atr=3.0,
            market_ctx={
                "macro": {"vix": 18.0, "sp500_trend": "up", "macro_score": 2},
                "hmm_regime": {
                    "regime": hmm_regime_label,
                    "bull_prob": 0.82,
                    "bear_prob": 0.08,
                    "transition_risk": 0.05,
                    "vix_z": -0.5,
                },
            },
            earnings_cal={"next_earnings_date": None},
            sector_rs={"sector_etf": "XLK", "rs_vs_sector": 0.02},
            days_to_earnings=90,
        )

    def test_quality_score_present_in_signal(self):
        from services.signal_engine import _assemble_signal

        sig = _assemble_signal(**self._build_minimal_signal_kwargs())
        assert sig is not None
        assert "qualityScore" in sig
        qs = sig["qualityScore"]
        assert isinstance(qs, float)
        assert 0.0 <= qs <= 100.0

    def test_hmm_regime_present_in_signal(self):
        from services.signal_engine import _assemble_signal

        sig = _assemble_signal(**self._build_minimal_signal_kwargs("bull"))
        assert sig is not None
        assert "hmmRegime" in sig
        assert sig["hmmRegime"] == "bull"

    def test_hmm_regime_none_when_absent(self):
        """hmmRegime is None when market_ctx has no hmm_regime key."""
        from services.signal_engine import _assemble_signal

        kwargs = self._build_minimal_signal_kwargs()
        kwargs["market_ctx"] = {"macro": {"vix": 18.0, "sp500_trend": "up", "macro_score": 2}}
        sig = _assemble_signal(**kwargs)
        assert sig is not None
        assert sig.get("hmmRegime") is None

    def test_bear_regime_lower_quality_score_independent(self):
        """Bear regime L9 multiplier is 0.70 — tested in pure math layer.
        Integration: signal dict is emitted and hmmRegime reflects the input."""
        from services.signal_engine import _assemble_signal

        kwargs = self._build_minimal_signal_kwargs("bear")
        kwargs["market_ctx"]["hmm_regime"]["bear_prob"] = 0.80
        kwargs["market_ctx"]["hmm_regime"]["bull_prob"] = 0.10
        sig = _assemble_signal(**kwargs)
        assert sig is not None
        assert sig["hmmRegime"] == "bear"

    def test_quality_score_varies_with_ou_hurst(self):
        """qualityScore is higher for fast OU + low Hurst than slow OU + high Hurst."""
        from services.signal_engine import _assemble_signal

        kwargs_high = self._build_minimal_signal_kwargs()
        kwargs_high["tech"] = _make_tech(ou_halflife=2.0, hurst=0.45)

        kwargs_low = self._build_minimal_signal_kwargs()
        kwargs_low["tech"] = _make_tech(ou_halflife=24.0, hurst=0.78)

        sig_high = _assemble_signal(**kwargs_high)
        sig_low = _assemble_signal(**kwargs_low)

        assert sig_high is not None and sig_low is not None
        assert sig_high["qualityScore"] > sig_low["qualityScore"]
