"""
Tests for pure functions in services/options.py and services/eightk_events.py.

Functions tested (all pure/sync, no network, no DB):
  options.py:
    - _bs_gamma(S, K, T, sigma)
    - _bs_vanna(S, K, T, sigma)
    - _bs_charm(S, K, T, sigma)
    - compute_dealer_positioning(spot, options_chain)
    - score_options(opt)

  eightk_events.py:
    - _parse_ceo_signal(text)
"""

import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ── options.py ────────────────────────────────────────────────────────────────

from services.options import _bs_charm, _bs_gamma, _bs_vanna, compute_dealer_positioning, score_options


class TestBsGamma:
    def test_atm_call_positive_gamma(self):
        """ATM option has positive gamma."""
        g = _bs_gamma(S=100, K=100, T=0.25, sigma=0.20)
        assert g > 0

    def test_gamma_positive_always(self):
        """Gamma is always positive for calls and puts."""
        g = _bs_gamma(S=110, K=100, T=0.5, sigma=0.30)
        assert g > 0

    def test_zero_time_returns_zero(self):
        """T=0 → gamma=0 (guard)."""
        assert _bs_gamma(S=100, K=100, T=0, sigma=0.20) == 0.0

    def test_zero_sigma_returns_zero(self):
        """sigma=0 → gamma=0 (guard)."""
        assert _bs_gamma(S=100, K=100, T=0.25, sigma=0) == 0.0

    def test_zero_spot_returns_zero(self):
        assert _bs_gamma(S=0, K=100, T=0.25, sigma=0.20) == 0.0

    def test_zero_strike_returns_zero(self):
        assert _bs_gamma(S=100, K=0, T=0.25, sigma=0.20) == 0.0

    def test_higher_sigma_lower_gamma_atm(self):
        """Higher IV → lower gamma for ATM (peak gamma is narrower)."""
        g_low = _bs_gamma(S=100, K=100, T=0.25, sigma=0.10)
        g_high = _bs_gamma(S=100, K=100, T=0.25, sigma=0.50)
        assert g_low > g_high


class TestBsVanna:
    def test_returns_float(self):
        v = _bs_vanna(S=100, K=100, T=0.25, sigma=0.20)
        assert isinstance(v, float)

    def test_zero_time_returns_zero(self):
        assert _bs_vanna(S=100, K=100, T=0, sigma=0.20) == 0.0

    def test_zero_sigma_returns_zero(self):
        assert _bs_vanna(S=100, K=100, T=0.25, sigma=0) == 0.0

    def test_zero_spot_returns_zero(self):
        assert _bs_vanna(S=0, K=100, T=0.25, sigma=0.20) == 0.0

    def test_atm_vanna_near_zero(self):
        """ATM options have d2 ≈ 0 → vanna ≈ 0 for ATM at-the-money."""
        v = _bs_vanna(S=100, K=100, T=0.5, sigma=0.20)
        assert abs(v) < 1.0  # vanna for ATM is small but not exactly 0


class TestBsCharm:
    def test_returns_float(self):
        c = _bs_charm(S=100, K=100, T=0.25, sigma=0.20)
        assert isinstance(c, float)

    def test_zero_time_returns_zero(self):
        assert _bs_charm(S=100, K=100, T=0, sigma=0.20) == 0.0

    def test_zero_sigma_returns_zero(self):
        assert _bs_charm(S=100, K=100, T=0.25, sigma=0) == 0.0

    def test_zero_spot_returns_zero(self):
        assert _bs_charm(S=0, K=100, T=0.25, sigma=0.20) == 0.0

    def test_result_is_per_day(self):
        """Charm is already divided by 365 — should be small for typical inputs."""
        c = _bs_charm(S=100, K=100, T=0.25, sigma=0.20)
        assert abs(c) < 0.1  # per-day value should be small


class TestComputeDealerPositioning:
    def _basic_chain(self, n_calls=1, n_puts=1):
        contracts = []
        for _ in range(n_calls):
            contracts.append({"strike": 100, "expiry_days": 30, "iv": 0.25, "oi": 500, "option_type": "call"})
        for _ in range(n_puts):
            contracts.append({"strike": 95, "expiry_days": 30, "iv": 0.25, "oi": 500, "option_type": "put"})
        return contracts

    def test_empty_chain_neutral(self):
        result = compute_dealer_positioning(100.0, [])
        assert result["net_vanna"] == 0.0
        assert result["net_charm"] == 0.0
        assert result["vanna_signal"] == "neutral"

    def test_returns_expected_keys(self):
        result = compute_dealer_positioning(100.0, self._basic_chain())
        for key in ("net_vanna", "net_charm", "vanna_signal", "charm_signal", "interpretation"):
            assert key in result

    def test_oi_below_threshold_filtered(self):
        """Contracts with OI below oi_threshold are excluded."""
        chain = [{"strike": 100, "expiry_days": 30, "iv": 0.25, "oi": 50, "option_type": "call"}]
        result = compute_dealer_positioning(100.0, chain, oi_threshold=100)
        assert result["net_vanna"] == 0.0

    def test_put_heavy_chain_bullish_vanna(self):
        """More puts than calls → dealers net long puts → positive vanna (bullish)."""
        chain = [
            {"strike": 95, "expiry_days": 30, "iv": 0.30, "oi": 1000, "option_type": "put"},
            {"strike": 95, "expiry_days": 30, "iv": 0.30, "oi": 1000, "option_type": "put"},
        ]
        result = compute_dealer_positioning(100.0, chain)
        assert result["net_vanna"] != 0.0

    def test_signal_is_valid_string(self):
        result = compute_dealer_positioning(100.0, self._basic_chain())
        assert result["vanna_signal"] in ("bullish", "bearish", "neutral")
        assert result["charm_signal"] in ("bullish", "bearish", "neutral")

    def test_interpretation_is_string(self):
        result = compute_dealer_positioning(100.0, self._basic_chain())
        assert isinstance(result["interpretation"], str)


class TestScoreOptions:
    def test_empty_dict_returns_zero(self):
        score, rationale = score_options({})
        assert score == 0.0
        assert rationale == []

    def test_none_dict_returns_zero(self):
        score, rationale = score_options(None)
        assert score == 0.0
        assert rationale == []

    def test_extreme_put_call_ratio_bullish(self):
        """P/C > 2.0 → contrarian bullish +10."""
        score, rationale = score_options({"pc_ratio": 2.5})
        assert score == 10
        assert any("Contrarian Bullish" in r["head"] for r in rationale)

    def test_moderate_put_call_ratio_small_bullish(self):
        """P/C 1.4–2.0 → small +5 boost."""
        score, rationale = score_options({"pc_ratio": 1.6})
        assert score == 5
        assert rationale == []

    def test_extreme_call_put_ratio_bearish(self):
        """P/C < 0.45 → call mania -12."""
        score, rationale = score_options({"pc_ratio": 0.30})
        assert score == -12
        assert any("Contrarian Bearish" in r["head"] for r in rationale)

    def test_moderately_low_pc_ratio(self):
        """P/C 0.45–0.65 → -6."""
        score, rationale = score_options({"pc_ratio": 0.55})
        assert score == -6

    def test_call_sweep_adds_score(self):
        """Large call sweep → positive score + rationale."""
        sweep = [
            {"strike": 150, "vol": 5000, "oi": 1000, "vol_oi": 5.0, "itm": False, "expiry": "2024-02-16", "iv": 0.30}
        ]
        score, rationale = score_options({"sweep_calls": sweep})
        assert score > 0
        assert any("Call Sweep" in r["head"] for r in rationale)

    def test_put_sweep_informational_no_penalty(self):
        """Put sweep is informational since 2026-07-15 (penalty neutralized —
        delivered MR-BUY cohort ran +10.2pp above baseline, N=160)."""
        sweep = [
            {"strike": 140, "vol": 5000, "oi": 1000, "vol_oi": 5.0, "itm": False, "expiry": "2024-02-16", "iv": 0.30}
        ]
        score, rationale = score_options({"sweep_puts": sweep})
        assert score == 0
        assert any("Put Sweep" in r["head"] for r in rationale)

    def test_otm_call_surge_bullish(self):
        """OTM call volume > 65% of total call vol and > 500 → +6."""
        score, rationale = score_options({"otm_call_vol": 800, "call_vol": 1000})
        assert score == 6
        assert any("OTM Call" in r["head"] for r in rationale)

    def test_otm_put_spike_informational(self):
        """OTM put spike is informational since 2026-07-15 (penalty neutralized —
        delivered MR-BUY cohort ran +4.6pp above baseline, N=241)."""
        score, rationale = score_options({"otm_put_vol": 800, "put_vol": 1000})
        assert score == 0
        assert any("OTM Put" in r["head"] for r in rationale)

    def test_combined_signals(self):
        """Multiple signals combine correctly."""
        score, rationale = score_options(
            {
                "pc_ratio": 2.5,  # +10
                "otm_call_vol": 800,
                "call_vol": 1000,  # +6
            }
        )
        assert score == 16
        assert len(rationale) >= 2

    def test_unusual_vol_no_sweeps_bullish(self):
        """uv > 3.0, no sweeps, pc=0.8 (no pc signal) → +6 bullish unusual vol."""
        score, rationale = score_options(
            {
                "unusual_vol_ratio": 4.0,
                "pc_ratio": 0.8,
                "sweep_calls": [],
                "sweep_puts": [],
            }
        )
        # pc=0.8: falls between 0.65 and 1.0 → no pc_ratio delta
        # unusual_vol bias = +1 (pc < 1.0) → score += 6
        assert score == 6

    def test_unusual_vol_no_sweeps_bearish(self):
        """uv > 3.0, no sweeps, pc > 1.0 → -6 bearish."""
        score, rationale = score_options(
            {
                "unusual_vol_ratio": 4.0,
                "pc_ratio": 1.2,
            }
        )
        assert score == -6

    def test_iv_term_spike_adds_rationale(self):
        """iv_term_spike > 1.5 → adds warning rationale."""
        score, rationale = score_options({"iv_term_spike": 2.0})
        assert any("IV Spike" in r["head"] for r in rationale)

    def test_low_iv_high_volume_bonus(self):
        """Low IV < 0.20 with uv > 2 → +3 score."""
        score, rationale = score_options({"avg_iv": 0.15, "unusual_vol_ratio": 2.5})
        assert score == 3

    def test_very_high_iv_adds_warning(self):
        """IV > 0.70 → warning rationale (no score change)."""
        score, rationale = score_options({"avg_iv": 0.80})
        assert any("High Implied Volatility" in r["head"] for r in rationale)

    def test_high_iv_rank_expensive(self):
        """IV Rank >= 80 → expensive volatility warning."""
        score, rationale = score_options({"iv_rank": 85})
        assert any("Expensive Volatility" in r["head"] for r in rationale)

    def test_low_iv_rank_cheap(self):
        """IV Rank <= 20 → +4 cheap volatility bonus."""
        score, rationale = score_options({"iv_rank": 15})
        assert score == 4
        assert any("Cheap Volatility" in r["head"] for r in rationale)

    def test_high_put_skew_bearish(self):
        """Put skew > 0.10 → -4."""
        score, rationale = score_options({"skew_25d": 0.15})
        assert score == -4

    def test_negative_gex_bearish(self):
        """GEX < -0.5B → -3."""
        score, rationale = score_options({"gex": -1_000_000_000})
        assert score == -3

    def test_positive_gex_neutral_score(self):
        """GEX > 0.5B → rationale only, no score change."""
        score, rationale = score_options({"gex": 1_000_000_000})
        assert score == 0
        assert any("GEX" in r["head"] for r in rationale)


# ── eightk_events.py ─────────────────────────────────────────────────────────

from services.eightk_events import _parse_ceo_signal


class TestParseCeoSignal:
    def test_resignation_is_departure(self):
        pts, label = _parse_ceo_signal("CEO John Doe to resign effective immediately.")
        assert pts == -6.0
        assert "departure" in label.lower() or "resign" in label.lower()

    def test_departure_keyword(self):
        pts, label = _parse_ceo_signal("CFO departs after quarterly results.")
        assert pts == -6.0

    def test_step_down_is_departure(self):
        pts, label = _parse_ceo_signal("The President will step down on Friday.")
        assert pts == -6.0

    def test_appointment_is_positive(self):
        pts, label = _parse_ceo_signal("Board appoints Jane Smith as new CEO.")
        assert pts == 3.0
        assert "appointed" in label.lower() or "appoint" in label.lower()

    def test_hired_is_positive(self):
        pts, label = _parse_ceo_signal("Company hires industry veteran as CFO.")
        assert pts == 3.0

    def test_named_as_positive(self):
        pts, label = _parse_ceo_signal("Smith named interim CEO effective today.")
        assert pts == 3.0

    def test_neutral_text_returns_zero(self):
        pts, label = _parse_ceo_signal("Quarterly earnings call scheduled for next week.")
        assert pts == 0.0
        assert label == ""

    def test_empty_text_returns_zero(self):
        pts, label = _parse_ceo_signal("")
        assert pts == 0.0
        assert label == ""

    def test_case_insensitive(self):
        """Keywords match regardless of case."""
        pts, _ = _parse_ceo_signal("THE CEO RESIGNED TODAY.")
        assert pts == -6.0

    def test_departure_takes_priority_over_appoint(self):
        """When both departure and appointment keywords appear, departure wins."""
        pts, _ = _parse_ceo_signal("CEO will resign after new CEO is appointed.")
        assert pts == -6.0
