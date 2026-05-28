"""
Tests for pure functions across several service modules that each have
small but testable pure helpers:

  - services/fear_greed.py: _classify(), _neutral_result()
  - services/eightk_events.py: _ITEM_MAP constant, cache behavior
  - services/massive_economy.py: pure parsing helpers
  - services/massive_options.py: pure scoring helpers
  - services/massive_analyst.py: pure scoring helpers
  - services/polygon_indicators.py: pure helpers
"""

import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# services/fear_greed.py — _classify and _neutral_result
# ─────────────────────────────────────────────────────────────────────────────

from services.fear_greed import _classify, _neutral_result


class TestFearGreedClassify:
    def test_extreme_fear_low_score(self):
        label, sentiment, bias = _classify(10.0)
        assert label == "Extreme Fear"
        assert sentiment == "pos"  # contrarian: oversold = buy dip
        assert bias == 15

    def test_fear_range(self):
        label, sentiment, bias = _classify(35.0)
        assert label == "Fear"
        assert bias == 7

    def test_neutral_range(self):
        label, sentiment, bias = _classify(50.0)
        assert label == "Neutral"
        assert bias == 0

    def test_greed_range(self):
        label, sentiment, bias = _classify(65.0)
        assert label == "Greed"
        assert sentiment == "neg"
        assert bias == -5

    def test_extreme_greed(self):
        label, sentiment, bias = _classify(85.0)
        assert label == "Extreme Greed"
        assert bias == -13

    def test_boundary_25_is_fear(self):
        label, _, _ = _classify(25.0)
        assert label == "Fear"

    def test_boundary_0_extreme_fear(self):
        label, _, _ = _classify(0.0)
        assert label == "Extreme Fear"

    def test_score_above_100_returns_neutral_default(self):
        """Scores outside all bands fall back to default."""
        label, sentiment, bias = _classify(200.0)
        assert label == "Neutral"
        assert bias == 0


class TestFearGreedNeutralResult:
    def test_returns_dict(self):
        result = _neutral_result()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = _neutral_result()
        for key in ("score", "label", "sentiment", "score_bias", "prev_close", "prev_1w", "prev_1m"):
            assert key in result

    def test_score_is_50(self):
        result = _neutral_result()
        assert result["score"] == 50.0

    def test_all_prev_values_are_50(self):
        result = _neutral_result()
        assert result["prev_close"] == 50.0
        assert result["prev_1w"] == 50.0
        assert result["prev_1m"] == 50.0


# ─────────────────────────────────────────────────────────────────────────────
# services/eightk_events.py — _ITEM_MAP structure + score clamping
# ─────────────────────────────────────────────────────────────────────────────

from services.eightk_events import _ITEM_MAP


class TestItemMap:
    def test_item_map_is_dict(self):
        assert isinstance(_ITEM_MAP, dict)

    def test_key_101_is_positive(self):
        pts, label, sentiment = _ITEM_MAP["1.01"]
        assert pts > 0

    def test_key_102_is_negative(self):
        pts, label, sentiment = _ITEM_MAP["1.02"]
        assert pts < 0

    def test_key_502_is_zero(self):
        """5.02 executive change — score is 0 base (parsed separately)."""
        pts, label, sentiment = _ITEM_MAP["5.02"]
        assert pts == 0

    def test_all_items_have_three_elements(self):
        for k, v in _ITEM_MAP.items():
            assert len(v) == 3, f"Item {k} should have (pts, label, sentiment)"


# ─────────────────────────────────────────────────────────────────────────────
# services/massive_options.py — score_option_chain pure function
# ─────────────────────────────────────────────────────────────────────────────

from services.massive_options import score_option_chain


class TestScoreOptionChain:
    def test_empty_signals_returns_zero(self):
        score, rationale = score_option_chain({}, 100.0, "BUY")
        assert score == 0.0
        assert rationale == []

    def test_none_signals_returns_zero(self):
        score, rationale = score_option_chain(None, 100.0, "BUY")
        assert score == 0.0
        assert rationale == []

    def test_positive_gex_buy_penalty(self):
        """GEX > 2M and action=BUY → -3 (pinning risk)."""
        score, rationale = score_option_chain({"net_gex": 5.0}, 100.0, "BUY")
        assert score == -3.0
        assert any("GEX" in r["head"] for r in rationale)

    def test_negative_gex_buy_bonus(self):
        """GEX < -2M and action=BUY → +3 (momentum fuel)."""
        score, rationale = score_option_chain({"net_gex": -5.0}, 100.0, "BUY")
        assert score == 3.0

    def test_elevated_put_skew_bullish(self):
        """Skew > 8 → +4 contrarian bullish."""
        score, rationale = score_option_chain({"skew_25d": 10.0}, 100.0, "BUY")
        assert score == 4.0

    def test_inverted_skew_bearish(self):
        """Skew < -4 → -3."""
        score, rationale = score_option_chain({"skew_25d": -5.0}, 100.0, "SELL")
        assert score == -3.0

    def test_max_pain_adds_rationale(self):
        """Max pain > 3% from spot → adds rationale about gravitational pull."""
        score, rationale = score_option_chain({"max_pain": 110.0}, 100.0, "BUY")
        assert any("Max Pain" in r["head"] for r in rationale)

    def test_max_pain_close_to_spot_no_rationale(self):
        """Max pain within 3% → no rationale added."""
        score, rationale = score_option_chain({"max_pain": 101.0}, 100.0, "BUY")
        assert not any("Max Pain" in r["head"] for r in rationale)


# ─────────────────────────────────────────────────────────────────────────────
# services/polygon_indicators.py — pure helper functions
# ─────────────────────────────────────────────────────────────────────────────

from services.polygon_indicators import blend_rsi, polygon_sma_crossover


class TestBlendRsi:
    def test_both_available_weighted_blend(self):
        """60% Polygon + 40% pandas."""
        result = blend_rsi(pandas_rsi=40.0, polygon_rsi=50.0)
        expected = round(0.6 * 50.0 + 0.4 * 40.0, 2)
        assert result == expected

    def test_only_polygon_rsi(self):
        """Only Polygon RSI → returns polygon value."""
        result = blend_rsi(pandas_rsi=None, polygon_rsi=55.0)
        assert result == 55.0

    def test_only_pandas_rsi(self):
        """Only pandas RSI → returns pandas value."""
        result = blend_rsi(pandas_rsi=45.0, polygon_rsi=None)
        assert result == 45.0

    def test_both_none_returns_none(self):
        result = blend_rsi(pandas_rsi=None, polygon_rsi=None)
        assert result is None


class TestPolygonSmaCrossover:
    def test_empty_indicators_returns_empty(self):
        result = polygon_sma_crossover({}, 100.0)
        assert result == {}

    def test_above_200_true(self):
        result = polygon_sma_crossover({"sma200": 90.0}, 100.0)
        assert result["above_200"] is True

    def test_above_200_false(self):
        result = polygon_sma_crossover({"sma200": 110.0}, 100.0)
        assert result["above_200"] is False

    def test_golden_cross_setup(self):
        result = polygon_sma_crossover({"sma50": 105.0, "sma200": 100.0}, 106.0)
        assert result["golden_cross_setup"] is True

    def test_pct_from_200(self):
        result = polygon_sma_crossover({"sma200": 100.0}, 110.0)
        assert result["pct_from_200"] == pytest.approx(10.0)

    def test_no_sma200_pct_is_none(self):
        result = polygon_sma_crossover({"sma50": 100.0}, 110.0)
        assert result.get("pct_from_200") is None
