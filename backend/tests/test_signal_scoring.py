"""
Tests for pure scoring functions in services/signal_scoring.py.

Functions under test:
  - score_oscillators(tech, rsi)
  - score_macd(hist, hist_p)
  - score_ema_cross(tech)
  - score_obv_adx(tech, running_score)
  - score_moving_averages(price, sma50, sma200, poly_ind)
"""
import sys
import os
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.signal_scoring import (
    score_oscillators,
    score_macd,
    score_ema_cross,
    score_obv_adx,
    score_moving_averages,
)


# ── score_oscillators ─────────────────────────────────────────────────────────

class TestScoreOscillators:

    def test_rsi_oversold_below_30(self):
        delta, rationale, dominant = score_oscillators({}, rsi=25.0)
        assert delta == 20
        assert dominant == "rsi"
        assert any("Oversold" in r["head"] for r in rationale)

    def test_rsi_weakening_30_to_40(self):
        delta, rationale, dominant = score_oscillators({}, rsi=35.0)
        assert delta == 10
        assert dominant is None
        assert any("Weakening" in r["head"] for r in rationale)

    def test_rsi_overbought_above_70(self):
        delta, rationale, dominant = score_oscillators({}, rsi=75.0)
        assert delta == -20
        assert dominant == "rsi"
        assert any("Overbought" in r["head"] for r in rationale)

    def test_rsi_elevated_60_to_70(self):
        delta, rationale, dominant = score_oscillators({}, rsi=65.0)
        assert delta == -10
        assert dominant is None

    def test_rsi_neutral_no_delta(self):
        """RSI in neutral zone (40–60) should produce no delta."""
        delta, rationale, dominant = score_oscillators({}, rsi=50.0)
        assert delta == 0
        assert dominant is None

    def test_rsi_none_no_effect(self):
        delta, rationale, dominant = score_oscillators({}, rsi=None)
        assert delta == 0
        assert rationale == []
        assert dominant is None

    def test_stochastic_bullish_cross_oversold(self):
        tech = {"stoch_k": 15.0, "stoch_d": 10.0, "stoch_k_prev": 9.0, "stoch_d_prev": 12.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == 10
        assert any("Bullish Cross" in r["head"] for r in rationale)

    def test_stochastic_bearish_cross_overbought(self):
        tech = {"stoch_k": 85.0, "stoch_d": 90.0, "stoch_k_prev": 92.0, "stoch_d_prev": 88.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == -10
        assert any("Bearish Cross" in r["head"] for r in rationale)

    def test_stochastic_oversold_no_cross(self):
        tech = {"stoch_k": 20.0, "stoch_d": 25.0, "stoch_k_prev": 18.0, "stoch_d_prev": 22.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == 5
        assert any("Oversold" in r["head"] for r in rationale)

    def test_williams_r_oversold(self):
        tech = {"williams_r": -85.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == 6
        assert any("Williams" in r["head"] for r in rationale)

    def test_williams_r_overbought(self):
        tech = {"williams_r": -10.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == -6

    def test_cci_extreme_oversold(self):
        tech = {"cci": -160.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == 7
        assert any("CCI" in r["head"] for r in rationale)

    def test_cci_extreme_overbought(self):
        tech = {"cci": 160.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == -7

    def test_cci_moderately_oversold(self):
        tech = {"cci": -120.0}
        delta, rationale, _ = score_oscillators(tech, rsi=None)
        assert delta == 3

    def test_empty_tech_dict_rsi_none_zero(self):
        delta, rationale, dominant = score_oscillators({}, rsi=None)
        assert delta == 0
        assert rationale == []
        assert dominant is None


# ── score_macd ─────────────────────────────────────────────────────────────────

class TestScoreMacd:

    def test_bullish_crossover(self):
        """Histogram crosses above zero: strong bull signal."""
        sd, td, rationale, dominant = score_macd(hist=0.01, hist_p=-0.01)
        assert sd == 22
        assert dominant == "macd"
        assert any("Bullish Crossover" in r["head"] for r in rationale)

    def test_bearish_crossover(self):
        """Histogram crosses below zero: strong bear signal."""
        sd, td, rationale, dominant = score_macd(hist=-0.01, hist_p=0.01)
        assert sd == -22
        assert dominant == "macd"

    def test_expanding_bullish(self):
        """Histogram positive and growing — trend delta, no score delta."""
        sd, td, rationale, dominant = score_macd(hist=0.05, hist_p=0.02)
        assert sd == 0
        assert td == 10
        assert dominant is None

    def test_expanding_bearish(self):
        """Histogram negative and falling — bearish trend delta."""
        sd, td, rationale, dominant = score_macd(hist=-0.05, hist_p=-0.02)
        assert sd == 0
        assert td == -10

    def test_no_crossover_shrinking(self):
        """Histogram positive but shrinking — no action."""
        sd, td, rationale, dominant = score_macd(hist=0.02, hist_p=0.05)
        assert sd == 0
        assert td == 0
        assert rationale == []

    def test_both_zero_no_action(self):
        sd, td, rationale, dominant = score_macd(hist=0.0, hist_p=0.0)
        assert sd == 0
        assert td == 0


# ── score_ema_cross ────────────────────────────────────────────────────────────

class TestScoreEmaCross:

    def test_bullish_cross(self):
        tech = {"ema8": 105.0, "ema21": 100.0, "ema8_prev": 99.0, "ema21_prev": 101.0}
        sd, td, rationale = score_ema_cross(tech)
        assert sd == 12
        assert any("Bullish Cross" in r["head"] for r in rationale)

    def test_bearish_cross(self):
        tech = {"ema8": 95.0, "ema21": 100.0, "ema8_prev": 101.0, "ema21_prev": 99.0}
        sd, td, rationale = score_ema_cross(tech)
        assert sd == -12
        assert any("Bearish Cross" in r["head"] for r in rationale)

    def test_ema8_above_ema21_no_cross(self):
        """EMA8 > EMA21 but no fresh cross — positive trend delta."""
        tech = {"ema8": 105.0, "ema21": 100.0, "ema8_prev": 103.0, "ema21_prev": 99.0}
        sd, td, rationale = score_ema_cross(tech)
        assert sd == 0
        assert td == 5

    def test_ema8_below_ema21_no_cross(self):
        """EMA8 < EMA21 but no fresh cross — negative trend delta."""
        tech = {"ema8": 95.0, "ema21": 100.0, "ema8_prev": 93.0, "ema21_prev": 101.0}
        sd, td, rationale = score_ema_cross(tech)
        assert sd == 0
        assert td == -5

    def test_missing_ema_values_zero_delta(self):
        """Missing EMA data → zero deltas."""
        sd, td, rationale = score_ema_cross({})
        assert sd == 0
        assert td == 0
        assert rationale == []


# ── score_obv_adx ──────────────────────────────────────────────────────────────

class TestScoreObvAdx:

    def test_obv_bullish_aligns_with_positive_score(self):
        tech = {"obv_above": True, "obv_slope": 100000}
        vd, td, rationale = score_obv_adx(tech, running_score=10.0)
        assert vd == 10   # bonus=10 when running_score > 0
        assert any("Bullish" in r["head"] for r in rationale)

    def test_obv_bullish_with_negative_score_lower_bonus(self):
        tech = {"obv_above": True, "obv_slope": 100000}
        vd, td, rationale = score_obv_adx(tech, running_score=-5.0)
        assert vd == 4    # bonus=4 when running_score <= 0

    def test_obv_bearish_aligns_with_negative_score(self):
        tech = {"obv_above": False, "obv_slope": -100000}
        vd, td, rationale = score_obv_adx(tech, running_score=-10.0)
        assert vd == -10

    def test_adx_strong_uptrend(self):
        tech = {"adx": 30.0, "adx_plus_di": 25.0, "adx_minus_di": 15.0}
        vd, td, rationale = score_obv_adx(tech, running_score=0)
        assert td == 8
        assert any("Uptrend" in r["head"] for r in rationale)

    def test_adx_strong_downtrend(self):
        tech = {"adx": 30.0, "adx_plus_di": 15.0, "adx_minus_di": 25.0}
        vd, td, rationale = score_obv_adx(tech, running_score=0)
        assert td == -8

    def test_adx_weak_no_delta(self):
        """ADX below 25 → no trend delta."""
        tech = {"adx": 20.0, "adx_plus_di": 20.0, "adx_minus_di": 10.0}
        vd, td, rationale = score_obv_adx(tech, running_score=0)
        assert td == 0

    def test_empty_tech_zero_deltas(self):
        vd, td, rationale = score_obv_adx({}, running_score=0)
        assert vd == 0
        assert td == 0
        assert rationale == []


# ── score_moving_averages ──────────────────────────────────────────────────────

class TestScoreMovingAverages:

    def test_above_sma200_bullish(self):
        # price must be > sma200 * 1.01 to trigger the bullish branch
        ma_delta, rationale = score_moving_averages(205.0, sma50=None, sma200=200.0, poly_ind={})
        assert ma_delta > 0
        assert any("200-DMA" in r["head"] for r in rationale)

    def test_below_sma200_bearish(self):
        ma_delta, rationale = score_moving_averages(195.0, sma50=None, sma200=200.0, poly_ind={})
        assert ma_delta < 0

    def test_golden_cross_bonus(self):
        """SMA50 > SMA200 → Golden Cross bonus."""
        ma_delta, rationale = score_moving_averages(
            200.0, sma50=210.0, sma200=200.0, poly_ind={}
        )
        assert any("Golden Cross" in r["head"] for r in rationale)

    def test_death_cross_penalty(self):
        """SMA50 < SMA200 → Death Cross penalty."""
        ma_delta, rationale = score_moving_averages(
            200.0, sma50=190.0, sma200=200.0, poly_ind={}
        )
        assert any("Death Cross" in r["head"] for r in rationale)

    def test_ema200_double_bullish(self):
        """Price above both EMA200 and SMA200 → double confirmation."""
        poly_ind = {"ema200": 195.0}
        ma_delta, rationale = score_moving_averages(
            200.0, sma50=None, sma200=195.0, poly_ind=poly_ind
        )
        # both confirmations should add +3
        assert any("Double Bullish" in r["head"] for r in rationale)

    def test_ema200_double_bearish(self):
        poly_ind = {"ema200": 210.0}
        ma_delta, rationale = score_moving_averages(
            200.0, sma50=None, sma200=210.0, poly_ind=poly_ind
        )
        assert any("Double Bearish" in r["head"] for r in rationale)

    def test_no_sma_data_zero_delta(self):
        ma_delta, rationale = score_moving_averages(200.0, sma50=None, sma200=None, poly_ind={})
        assert ma_delta == 0
        assert rationale == []

    def test_sma50_above_price_adds_negative(self):
        """Price below SMA50 → negative delta."""
        ma_delta, rationale = score_moving_averages(90.0, sma50=100.0, sma200=None, poly_ind={})
        assert ma_delta == -8

    def test_sma50_below_price_adds_positive(self):
        """Price above SMA50 → positive delta."""
        ma_delta, rationale = score_moving_averages(110.0, sma50=100.0, sma200=None, poly_ind={})
        assert ma_delta == 8
