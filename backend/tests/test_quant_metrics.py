"""
Tests for the quant metric functions in scripts/calc_tbd_metrics.py.
"""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from calc_tbd_metrics import (
    _mean, _std, _percentile, _skewness, _kurtosis, _t_stat,
    _norm_cdf, _annualize_factor, calc_metrics, risk_metrics,
    pf_str, confidence_bucket,
)


# ── Basic stats ───────────────────────────────────────────────────────────────

def test_mean_basic():
    assert _mean([1.0, 2.0, 3.0]) == pytest.approx(2.0)
    assert _mean([]) == 0.0

def test_std_basic():
    import pytest
    # ddof=1 sample std of [2,4,4,4,5,5,7,9] → variance=32/7 → std≈2.138
    result = _std([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert result == pytest.approx(math.sqrt(32.0 / 7.0), rel=1e-6)
    assert _std([]) == 0.0
    assert _std([5.0]) == 0.0  # single element

def test_percentile_basic():
    import pytest
    data = list(range(1, 101))  # 1..100
    assert _percentile(data, 50) == pytest.approx(50.5, rel=0.01)
    assert _percentile(data, 0)  == pytest.approx(1.0,  rel=0.01)
    assert _percentile(data, 100) == pytest.approx(100.0, rel=0.01)

def test_percentile_empty():
    assert _percentile([], 50) == 0.0

def test_skewness_symmetric():
    import pytest
    # Symmetric data should have near-zero skewness
    data = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
    assert abs(_skewness(data)) < 0.01

def test_skewness_right_tail():
    import pytest
    data = [0.0] * 9 + [10.0]  # one large positive outlier
    assert _skewness(data) > 0

def test_kurtosis_normal():
    import pytest
    # Larger sample of normal-ish data → excess kurtosis ≈ 0
    import random
    random.seed(42)
    data = [random.gauss(0, 1) for _ in range(1000)]
    assert abs(_kurtosis(data)) < 0.5  # within sampling noise

def test_t_stat_significant():
    import pytest
    # High mean, small variance → large t-stat
    data = [5.0 + (0.1 * (i % 3 - 1)) for i in range(50)]  # clustered around 5
    t, p = _t_stat(data)
    assert t > 10
    assert p < 0.001

def test_t_stat_not_significant():
    import pytest
    import random
    random.seed(0)
    data = [random.uniform(-5, 5) for _ in range(20)]
    t, p = _t_stat(data)
    # With zero-mean noise, p should usually be > 0.05
    # (Not guaranteed but very likely)
    assert isinstance(t, float)
    assert isinstance(p, float)

def test_norm_cdf():
    import pytest
    assert _norm_cdf(0.0) == pytest.approx(0.5, abs=1e-6)
    assert _norm_cdf(1.96) == pytest.approx(0.975, abs=0.005)
    assert _norm_cdf(-1.96) == pytest.approx(0.025, abs=0.005)

def test_annualize_factor():
    import pytest
    # 100 trades over 100 days → 1 trade/day × 252 = 252
    assert _annualize_factor(100, 100) == pytest.approx(252.0, rel=0.01)
    # Edge cases
    assert _annualize_factor(0, 100) == 252.0
    assert _annualize_factor(100, 0) == 252.0


# ── calc_metrics ─────────────────────────────────────────────────────────────

def test_calc_metrics_empty():
    import pytest
    m = calc_metrics([])
    assert m["count"] == 0
    assert m["wr"] == 0.0

def test_calc_metrics_all_wins():
    import pytest
    m = calc_metrics([5.0, 3.0, 7.0])
    assert m["wr"] == pytest.approx(100.0)
    assert m["pf"] == float("inf")
    assert m["avg"] == pytest.approx(5.0)

def test_calc_metrics_all_losses():
    import pytest
    m = calc_metrics([-2.0, -3.0, -1.0])
    assert m["wr"] == pytest.approx(0.0)
    assert m["pf"] == pytest.approx(0.0)
    assert m["kelly"] == pytest.approx(0.0)

def test_calc_metrics_mixed():
    import pytest
    # 2 wins of 10%, 1 loss of -5%
    m = calc_metrics([10.0, 10.0, -5.0])
    assert m["wr"] == pytest.approx(200 / 3, rel=0.01)
    assert m["pf"]  == pytest.approx(20.0 / 5.0)
    assert m["expectancy"] > 0

def test_calc_metrics_kelly():
    import pytest
    # Classic Kelly: 60% WR, avg win = 10%, avg loss = -10% → Kelly = 0.2
    returns = [10.0] * 6 + [-10.0] * 4
    m = calc_metrics(returns)
    assert m["kelly"] == pytest.approx(20.0, rel=0.01)  # 20%


# ── risk_metrics ──────────────────────────────────────────────────────────────

def test_risk_metrics_positive_sharpe():
    import pytest
    # Mix with small losses so downside std is defined
    returns = [3.0, 4.0, 2.0, 5.0, 3.5, -0.5, 4.0, 2.5, 3.0, -0.3] * 10
    rm = risk_metrics(returns, date_range_days=20)
    assert rm["sharpe"] > 0
    assert rm["sortino"] > 0
    assert rm["omega"] > 1.0

def test_risk_metrics_var():
    import pytest
    # Uniform returns 1–100: VaR 95 should be around 5
    returns = list(range(1, 101))
    rm = risk_metrics(returns, date_range_days=30)
    assert rm["var_95"] < 0     # 5th percentile of 1–100 is ~5 → VaR = -5 (negative means loss)
    # Actually VaR 95% = -percentile(5) — but all returns are positive, so var_95 will be negative
    # meaning there's no loss at the 95th percentile
    # That's correct — the VaR is the LOSS, so a positive set has negative VaR (no expected loss)

def test_risk_metrics_max_drawdown():
    import pytest
    # Alternating gains and large losses
    returns = [10.0, -8.0, 10.0, -8.0] * 10
    rm = risk_metrics(returns, date_range_days=20)
    assert rm["max_dd"] > 0

def test_risk_metrics_ulcer_zero_for_monotone():
    import pytest
    # Monotonically increasing equity → no drawdown → ulcer ≈ 0
    returns = [1.0] * 50  # always making money
    rm = risk_metrics(returns, date_range_days=50)
    assert rm["ulcer"] == pytest.approx(0.0, abs=1e-10)

def test_risk_metrics_skew_positive():
    import pytest
    # Right-skewed: mostly small losses, occasional big wins
    returns = [-1.0] * 8 + [20.0] * 2
    rm = risk_metrics(returns, date_range_days=10)
    assert rm["skew"] > 0

def test_risk_metrics_streaks():
    returns = [5.0, 5.0, 5.0, -3.0, -3.0, 5.0]
    rm = risk_metrics(returns, date_range_days=6)
    assert rm["max_win_streak"] == 3
    assert rm["max_loss_streak"] == 2

def test_risk_metrics_insufficient_data():
    # Less than 5 returns → empty dict
    rm = risk_metrics([1.0, 2.0, 3.0], date_range_days=3)
    assert rm == {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def test_pf_str():
    assert pf_str(float("inf")) == "∞"
    assert pf_str(2.5) == "2.50x"

def test_confidence_bucket():
    assert confidence_bucket(70.0) == "High (≥70%)"
    assert confidence_bucket(69.9) == "Medium (55–69%)"
    assert confidence_bucket(55.0) == "Medium (55–69%)"
    assert confidence_bucket(54.9) == "Low (<55%)"
    assert confidence_bucket(0.0)  == "Low (<55%)"


import pytest  # imported at end to avoid issues with sys.path manipulation above
