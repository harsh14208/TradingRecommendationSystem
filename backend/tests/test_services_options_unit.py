"""Unit tests for services/options.py — pure math helpers and scoring."""
import math
from unittest.mock import MagicMock, patch

import pytest


# ── Black-Scholes greeks ──────────────────────────────────────────────────────

def test_bs_gamma_positive():
    from services.options import _bs_gamma
    g = _bs_gamma(S=100, K=100, T=0.25, sigma=0.20)
    assert g > 0
    assert isinstance(g, float)


def test_bs_gamma_zero_T():
    from services.options import _bs_gamma
    assert _bs_gamma(S=100, K=100, T=0, sigma=0.20) == 0.0


def test_bs_gamma_zero_sigma():
    from services.options import _bs_gamma
    assert _bs_gamma(S=100, K=100, T=0.25, sigma=0) == 0.0


def test_bs_gamma_zero_S():
    from services.options import _bs_gamma
    assert _bs_gamma(S=0, K=100, T=0.25, sigma=0.20) == 0.0


def test_bs_gamma_zero_K():
    from services.options import _bs_gamma
    assert _bs_gamma(S=100, K=0, T=0.25, sigma=0.20) == 0.0


def test_bs_gamma_atm():
    from services.options import _bs_gamma
    g_atm = _bs_gamma(S=100, K=100, T=0.25, sigma=0.20)
    g_itm = _bs_gamma(S=100, K=80, T=0.25, sigma=0.20)
    g_otm = _bs_gamma(S=100, K=120, T=0.25, sigma=0.20)
    assert g_atm > g_itm
    assert g_atm > g_otm


def test_bs_vanna_positive_skew():
    from services.options import _bs_vanna
    v = _bs_vanna(S=100, K=110, T=0.25, sigma=0.25)
    assert isinstance(v, float)


def test_bs_vanna_zero_guards():
    from services.options import _bs_vanna
    assert _bs_vanna(S=0, K=100, T=0.25, sigma=0.25) == 0.0
    assert _bs_vanna(S=100, K=0, T=0.25, sigma=0.25) == 0.0
    assert _bs_vanna(S=100, K=100, T=0, sigma=0.25) == 0.0
    assert _bs_vanna(S=100, K=100, T=0.25, sigma=0) == 0.0


def test_bs_charm_negative_call():
    from services.options import _bs_charm
    c = _bs_charm(S=100, K=100, T=0.25, sigma=0.20)
    assert isinstance(c, float)
    assert c != 0.0


def test_bs_charm_zero_guards():
    from services.options import _bs_charm
    assert _bs_charm(S=0, K=100, T=0.25, sigma=0.20) == 0.0
    assert _bs_charm(S=100, K=0, T=0.25, sigma=0.20) == 0.0
    assert _bs_charm(S=100, K=100, T=0, sigma=0.20) == 0.0
    assert _bs_charm(S=100, K=100, T=0.25, sigma=0) == 0.0


# ── compute_dealer_positioning ────────────────────────────────────────────────

def test_compute_dealer_positioning_empty():
    from services.options import compute_dealer_positioning
    result = compute_dealer_positioning(spot=100.0, options_chain=[])
    assert result["net_vanna"] == 0.0
    assert result["net_charm"] == 0.0
    assert result["vanna_signal"] == "neutral"
    assert result["charm_signal"] == "neutral"


def test_compute_dealer_positioning_below_threshold():
    from services.options import compute_dealer_positioning
    # OI below threshold (100) → skipped
    chain = [{"strike": 100, "expiry_days": 30, "iv": 0.2, "oi": 50, "option_type": "call"}]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain, oi_threshold=100)
    assert result["net_vanna"] == 0.0


def test_compute_dealer_positioning_call():
    from services.options import compute_dealer_positioning
    chain = [{"strike": 110, "expiry_days": 30, "iv": 0.25, "oi": 5000, "option_type": "call"}]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain)
    assert isinstance(result["net_vanna"], float)
    assert isinstance(result["net_charm"], float)
    assert result["vanna_signal"] in ("bullish", "bearish", "neutral")
    assert result["charm_signal"] in ("bullish", "bearish", "neutral")


def test_compute_dealer_positioning_put():
    from services.options import compute_dealer_positioning
    chain = [{"strike": 90, "expiry_days": 30, "iv": 0.25, "oi": 5000, "option_type": "put"}]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain)
    assert isinstance(result["interpretation"], str)


def test_compute_dealer_positioning_mixed_chain():
    from services.options import compute_dealer_positioning
    chain = [
        {"strike": 110, "expiry_days": 30, "iv": 0.25, "oi": 1000, "option_type": "call"},
        {"strike": 90, "expiry_days": 15, "iv": 0.30, "oi": 2000, "option_type": "put"},
    ]
    result = compute_dealer_positioning(spot=100.0, options_chain=chain)
    assert "net_vanna" in result


# ── score_options ─────────────────────────────────────────────────────────────

def test_score_options_empty():
    from services.options import score_options
    score, rationale = score_options({})
    assert score == 0.0
    assert rationale == []


def test_score_options_none():
    from services.options import score_options
    score, rationale = score_options(None)
    assert score == 0.0
    assert rationale == []


def test_score_options_extreme_pc_high():
    from services.options import score_options
    score, rationale = score_options({"pc_ratio": 2.5})
    assert score >= 10
    assert any("Put/Call" in r["head"] for r in rationale)


def test_score_options_extreme_pc_low():
    from services.options import score_options
    score, rationale = score_options({"pc_ratio": 0.3})
    assert score <= -10
    assert any("Call/Put" in r["head"] for r in rationale)


def test_score_options_moderate_pc():
    from services.options import score_options
    score_high, _ = score_options({"pc_ratio": 1.5})  # 1.4–2.0 → +5
    score_low, _ = score_options({"pc_ratio": 0.55})  # 0.45–0.65 → −6
    assert score_high > 0
    assert score_low < 0


def test_score_options_sweep_calls():
    from services.options import score_options
    opt = {
        "sweep_calls": [{"vol_oi": 3.0, "strike": 150, "itm": False,
                          "vol": 300, "oi": 100, "expiry": "2026-07-18", "iv": 0.25}]
    }
    score, rationale = score_options(opt)
    assert score > 0
    assert any("Call Sweep" in r["head"] for r in rationale)


def test_score_options_sweep_puts():
    from services.options import score_options
    opt = {
        "sweep_puts": [{"vol_oi": 3.0, "strike": 140, "itm": False,
                         "vol": 300, "oi": 100, "expiry": "2026-07-18", "iv": 0.25}]
    }
    score, rationale = score_options(opt)
    assert score < 0
    assert any("Put Sweep" in r["head"] for r in rationale)


def test_score_options_iv_spike():
    from services.options import score_options
    score, _ = score_options({"iv_term_spike": True})
    # IV term spike is a positive signal (front-month IV spike = fear spike = MR opportunity)
    assert isinstance(score, float)


def test_score_options_otm_call_skew():
    from services.options import score_options
    # High OTM call vol vs put vol → call-side mania
    score, _ = score_options({"otm_call_vol": 5000, "otm_put_vol": 100})
    assert score <= 0  # bearish (call-side mania)


def test_score_options_returns_tuple():
    from services.options import score_options
    result = score_options({"pc_ratio": 1.0, "avg_iv": 0.30})
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], float)
    assert isinstance(result[1], list)


# ── _ivh_load / _ivh_save ─────────────────────────────────────────────────────

def test_ivh_load_no_redis_empty():
    import services.options as opts
    opts._iv_history = {}
    opts._opt_redis = None
    from services.options import _ivh_load
    result = _ivh_load("AAPL")
    assert result == []


def test_ivh_load_local_cache():
    import services.options as opts
    opts._iv_history = {"AAPL": [0.25, 0.30, 0.28]}
    opts._opt_redis = None
    from services.options import _ivh_load
    result = _ivh_load("AAPL")
    assert result == [0.25, 0.30, 0.28]
    opts._iv_history = {}


def test_ivh_save_no_redis():
    import services.options as opts
    opts._opt_redis = None
    from services.options import _ivh_save
    _ivh_save("NVDA", [0.40, 0.42])
    assert opts._iv_history.get("NVDA") == [0.40, 0.42]
    del opts._iv_history["NVDA"]


def test_ivh_save_with_redis():
    import services.options as opts
    mock_redis = MagicMock()
    opts._opt_redis = mock_redis
    from services.options import _ivh_save
    _ivh_save("MSFT", [0.20])
    mock_redis.setex.assert_called_once()
    opts._opt_redis = None
    opts._iv_history.pop("MSFT", None)


def test_ivh_load_redis_error():
    import services.options as opts
    mock_redis = MagicMock()
    mock_redis.get.side_effect = Exception("redis down")
    opts._opt_redis = mock_redis
    opts._iv_history = {"AAPL": [0.25]}
    from services.options import _ivh_load
    result = _ivh_load("AAPL")
    assert result == [0.25]
    opts._opt_redis = None
    opts._iv_history = {}


# ── _opt_cache_get / _opt_cache_set ──────────────────────────────────────────

def test_opt_cache_get_miss():
    import services.options as opts
    opts._opt_cache = {}
    opts._opt_redis = None
    from services.options import _opt_cache_get
    assert _opt_cache_get("AAPL") is None


def test_opt_cache_set_and_get():
    import services.options as opts
    opts._opt_redis = None
    from services.options import _opt_cache_get, _opt_cache_set
    _opt_cache_set("AAPL", {"pc_ratio": 1.2})
    result = _opt_cache_get("AAPL")
    assert result is not None
    assert result["pc_ratio"] == 1.2
    opts._opt_cache.pop("AAPL", None)
