"""
Tests for pure helper functions in financial service modules:

  - services/massive_ratios.py: _val()
  - services/calibration.py: additional edge cases
  - services/signal_scoring.py: remaining coverage
  - services/technicals.py: pure helpers
"""
import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# services/massive_ratios.py — _val() extraction helper
# ─────────────────────────────────────────────────────────────────────────────

from services.massive_ratios import _val


class TestVal:

    def test_dict_with_value_key_returns_float(self):
        section = {"revenue": {"value": 1_000_000}}
        assert _val(section, "revenue") == 1_000_000.0

    def test_dict_with_none_value_returns_none(self):
        section = {"revenue": {"value": None}}
        assert _val(section, "revenue") is None

    def test_plain_numeric_value(self):
        section = {"revenue": 500_000}
        assert _val(section, "revenue") == 500_000.0

    def test_string_numeric_value(self):
        section = {"revenue": "750000"}
        assert _val(section, "revenue") == 750_000.0

    def test_missing_key_returns_none(self):
        assert _val({}, "revenue") is None

    def test_non_numeric_string_returns_none(self):
        section = {"revenue": "N/A"}
        assert _val(section, "revenue") is None

    def test_none_value_returns_none(self):
        section = {"revenue": None}
        assert _val(section, "revenue") is None

    def test_float_value_returned_as_float(self):
        section = {"margin": 0.2345}
        result = _val(section, "margin")
        assert result == pytest.approx(0.2345)
        assert isinstance(result, float)

    def test_negative_value(self):
        section = {"net_income": {"value": -250_000}}
        assert _val(section, "net_income") == -250_000.0

    def test_zero_value(self):
        section = {"debt": 0}
        assert _val(section, "debt") == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# services/signal_scoring.py — remaining coverage (stochastic/ADX combos)
# ─────────────────────────────────────────────────────────────────────────────

from services.signal_scoring import score_oscillators, score_obv_adx, score_moving_averages


class TestOscillatorEdgeCases:

    def test_stochastic_overbought_no_cross(self):
        """Stoch K > 75 but no bearish cross → -5 penalty."""
        tech = {"stoch_k": 80.0, "stoch_d": 70.0, "stoch_k_prev": 78.0, "stoch_d_prev": 72.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == -5

    def test_cci_moderately_overbought(self):
        """CCI > 100 but < 150 → -3."""
        tech = {"cci": 120.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == -3

    def test_stochastic_missing_prev_values_no_cross(self):
        """Missing prev stoch values → no cross signal, only level-based."""
        tech = {"stoch_k": 15.0, "stoch_d": 25.0, "stoch_k_prev": None, "stoch_d_prev": None}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        # stoch_k < 25 and no cross → +5
        assert delta == 5

    def test_williams_r_in_middle_no_signal(self):
        """Williams %R in -80 to -20 range → no signal."""
        tech = {"williams_r": -50.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == 0


class TestMovingAverageEdgeCases:

    def test_price_between_sma200_bands_no_signal(self):
        """Price within ±1% of SMA200 → no delta."""
        ma_delta, rationale = score_moving_averages(200.5, sma50=None, sma200=200.0, poly_ind={})
        # 200.5 / 200.0 = 1.0025 which is < 1.01 → no bullish signal
        # 200.5 / 200.0 * 0.99 = 198.0 < 200.5 so no bearish either
        assert ma_delta == 0

    def test_sma50_sma200_near_equal_no_cross_signal(self):
        """SMA50 ≈ SMA200 (within 0.5%) → no golden/death cross."""
        ma_delta, rationale = score_moving_averages(200.0, sma50=200.5, sma200=200.0, poly_ind={})
        # SMA50 > SMA200 * 1.005 → 200.5 > 201.0? No → no golden cross
        assert not any("Golden Cross" in r.get("head", "") for r in rationale)

    def test_poly_ind_none_no_ema200(self):
        """poly_ind=None → no EMA200 double-confirmation."""
        ma_delta, rationale = score_moving_averages(205.0, sma50=None, sma200=200.0, poly_ind=None)
        assert not any("Double" in r.get("head", "") for r in rationale)


class TestObvAdxEdgeCases:

    def test_obv_bearish_with_positive_score_lower_penalty(self):
        """OBV bearish but running_score > 0 → -4 (not -10)."""
        tech = {"obv_above": False, "obv_slope": -100000}
        vd, td, rationale = score_obv_adx(tech, running_score=5.0)
        assert vd == -4

    def test_adx_all_missing_no_delta(self):
        """ADX present but DI values missing → no delta."""
        tech = {"adx": 30.0}  # missing plus_di and minus_di
        vd, td, rationale = score_obv_adx(tech, running_score=0)
        assert td == 0


# ─────────────────────────────────────────────────────────────────────────────
# services/massive_options.py — additional score_option_chain paths
# ─────────────────────────────────────────────────────────────────────────────

from services.massive_options import score_option_chain


class TestScoreOptionChainEdgeCases:

    def test_positive_gex_sell_action_no_penalty(self):
        """GEX > 2M and action=SELL → no penalty (only BUY gets -3)."""
        score, rationale = score_option_chain({"net_gex": 5.0}, 100.0, "SELL")
        # score should be 0 for positive GEX when action=SELL
        assert score == 0.0

    def test_negative_gex_sell_action_no_bonus(self):
        """GEX < -2M and action=SELL → no bonus (only BUY gets +3)."""
        score, rationale = score_option_chain({"net_gex": -5.0}, 100.0, "SELL")
        assert score == 0.0

    def test_skew_within_range_no_signal(self):
        """Skew between -4 and 8 → no signal."""
        score, rationale = score_option_chain({"skew_25d": 3.0}, 100.0, "BUY")
        assert score == 0.0
        assert rationale == []

    def test_combined_gex_and_skew(self):
        """Positive GEX BUY (-3) + elevated skew (+4) = +1."""
        score, rationale = score_option_chain({"net_gex": 5.0, "skew_25d": 10.0}, 100.0, "BUY")
        assert score == 1.0


# ─────────────────────────────────────────────────────────────────────────────
# services/polygon_indicators.py — additional blend_rsi and sma_crossover
# ─────────────────────────────────────────────────────────────────────────────

from services.polygon_indicators import blend_rsi, polygon_sma_crossover


class TestBlendRsiEdgeCases:

    def test_equal_rsi_values_blend_same(self):
        """When both RSIs are equal, blend returns same value."""
        result = blend_rsi(50.0, 50.0)
        assert result == 50.0

    def test_blend_rounding(self):
        """Result is rounded to 2 decimal places."""
        result = blend_rsi(33.33, 66.67)
        assert result == round(0.6 * 66.67 + 0.4 * 33.33, 2)


class TestPolygonSmaCrossoverEdgeCases:

    def test_death_cross_setup(self):
        """SMA50 < SMA200 * 1.01 → death cross setup."""
        result = polygon_sma_crossover({"sma50": 95.0, "sma200": 100.0}, 94.0)
        assert result.get("death_cross_setup") is True

    def test_above_50_false(self):
        result = polygon_sma_crossover({"sma50": 110.0}, 100.0)
        assert result["above_50"] is False

    def test_above_20_true(self):
        result = polygon_sma_crossover({"sma20": 90.0}, 100.0)
        assert result["above_20"] is True

    def test_multiple_smas(self):
        result = polygon_sma_crossover({"sma200": 180.0, "sma50": 195.0, "sma20": 198.0}, 200.0)
        assert result["above_200"] is True
        assert result["above_50"] is True
        assert result["above_20"] is True
