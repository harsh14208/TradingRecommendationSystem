"""Unit tests for §99b sprt_monitor.py — Wald boundary cases."""

from __future__ import annotations

import math


from scripts.sprt_monitor import SPRTConfig, _sprt_llr, sprt_decision


class TestSPRTWaldBoundaries:
    """Known-value tests from Wald (1945)."""

    def test_wald_boundaries_alpha_05_beta_05(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05)
        # log(beta/(1-alpha)) = log(0.05/0.95) ≈ -2.944
        assert math.isclose(cfg.lower_boundary, math.log(0.05 / 0.95), rel_tol=1e-6)
        # log((1-beta)/alpha) = log(0.95/0.05) ≈ +2.944
        assert math.isclose(cfg.upper_boundary, math.log(0.95 / 0.05), rel_tol=1e-6)

    def test_wald_boundaries_symmetric(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05)
        assert math.isclose(cfg.lower_boundary, -cfg.upper_boundary, rel_tol=1e-6)

    def test_decision_at_exact_upper_boundary(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05)
        assert sprt_decision(cfg.upper_boundary, cfg) == "accept_h1"

    def test_decision_at_exact_lower_boundary(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05)
        assert sprt_decision(cfg.lower_boundary, cfg) == "accept_h0"

    def test_decision_inside_band(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05)
        mid = (cfg.lower_boundary + cfg.upper_boundary) / 2.0
        assert sprt_decision(mid, cfg) == "continue"

    def test_decision_zero_llr(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05)
        assert sprt_decision(0.0, cfg) == "continue"


class TestSPRTLLR:
    """Log-likelihood ratio computation."""

    def test_llr_empty_obs(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05, sigma=1.0)
        llr, sigma = _sprt_llr([], cfg)
        assert llr == 0.0
        assert sigma == 1.0

    def test_llr_single_obs(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05, sigma=1.0)
        # LLR = (1 - 0) / 1^2 * (0.5 - 0.5) = 0.0
        llr, sigma = _sprt_llr([0.5], cfg)
        assert math.isclose(llr, 0.0, abs_tol=1e-9)

    def test_llr_favours_h1(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05, sigma=1.0)
        # Observations above midpoint (0.5) favour H1
        llr, _ = _sprt_llr([1.0, 1.0, 1.0], cfg)
        assert llr > 0.0

    def test_llr_favours_h0(self) -> None:
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05, sigma=1.0)
        # Observations below midpoint (0.5) favour H0
        llr, _ = _sprt_llr([0.0, 0.0, 0.0], cfg)
        assert llr < 0.0

    def test_llr_crossing_threshold(self) -> None:
        """Simulate a trajectory that crosses the upper boundary."""
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05, sigma=1.0)
        # 20 observations at +1.5% should strongly favour H1
        llr, _ = _sprt_llr([1.5] * 20, cfg)
        assert llr > cfg.upper_boundary
        assert sprt_decision(llr, cfg) == "accept_h1"

    def test_llr_h0_acceptance(self) -> None:
        """Simulate a trajectory that crosses the lower boundary."""
        cfg = SPRTConfig(h0=0.0, h1=1.0, alpha=0.05, beta=0.05, sigma=1.0)
        # 20 observations at -1.5% should strongly favour H0
        llr, _ = _sprt_llr([-1.5] * 20, cfg)
        assert llr < cfg.lower_boundary
        assert sprt_decision(llr, cfg) == "accept_h0"
