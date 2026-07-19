"""
Tests for the performance snapshot system:
  - diff_snapshots() logic
  - _find_flagged() helper
  - CLI flag wiring (smoke test)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pytest
from calc_tbd_metrics import diff_snapshots

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _snap(win_rate=60.0, sharpe=5.0, avg=2.5, max_dd=2.0, phantom=10, stop_enforced_wr=55.0, brier=0.28):
    return {
        "returns": {"win_rate": win_rate, "avg": avg, "pf": 3.0, "kelly": 39.0},
        "risk": {
            "sharpe": sharpe,
            "sortino": 12.0,
            "max_dd": max_dd,
            "calmar": 300.0,
            "omega": 3.0,
            "recovery": 500.0,
            "ulcer": 0.5,
        },
        "tail": {"var_95": 6.8, "var_99": 10.0, "cvar_95": 8.7, "sigma": 7.0},
        "distribution": {
            "skew": 1.2,
            "kurt": 2.3,
            "t_stat": 8.0,
            "p_value": 0.0,
            "brier": brier,
            "max_win_streak": 16,
            "max_loss_streak": 8,
        },
        "trade_path": {
            "phantom_wins": phantom,
            "stop_enforced_wr": stop_enforced_wr,
            "hit_stop_pct": 45.0,
            "hit_target_pct": 38.0,
            "avg_mae": -6.0,
            "avg_mfe": 10.5,
            "capture_ratio": 0.41,
        },
        "by_style": {"position": {"n": 450, "win_rate": 61.0, "avg": 2.9, "sharpe": 1.6}},
        "by_month": {"2026-04": {"n": 336, "win_rate": 63.0, "avg": 3.0, "sharpe": 1.6}},
    }


# ── diff_snapshots ─────────────────────────────────────────────────────────────


def test_diff_identical_snapshots():
    s = _snap()
    d = diff_snapshots(s, s)
    # Every numeric leaf should have delta=0
    assert d["returns"]["win_rate"]["delta"] == 0
    assert d["risk"]["sharpe"]["delta"] == 0
    assert d["trade_path"]["phantom_wins"]["delta"] == 0


def test_diff_win_rate_improvement():
    before = _snap(win_rate=55.0)
    after = _snap(win_rate=60.0)
    d = diff_snapshots(before, after)
    wr = d["returns"]["win_rate"]
    assert wr["before"] == 55.0
    assert wr["after"] == 60.0
    assert wr["delta"] == pytest.approx(5.0)
    assert wr["flag"] is True  # 5pp >= threshold of 2pp


def test_diff_win_rate_small_change_no_flag():
    before = _snap(win_rate=60.0)
    after = _snap(win_rate=60.8)
    d = diff_snapshots(before, after)
    assert d["returns"]["win_rate"]["flag"] is False  # < 2pp threshold


def test_diff_sharpe_degradation_flagged():
    before = _snap(sharpe=0.20)
    after = _snap(sharpe=-0.15)
    d = diff_snapshots(before, after)
    sh = d["risk"]["sharpe"]
    assert sh["delta"] == pytest.approx(-0.35, abs=0.01)
    assert sh["flag"] is True  # abs(delta) = 0.35 >= threshold 0.3


def test_diff_sharpe_tiny_change_no_flag():
    before = _snap(sharpe=0.20)
    after = _snap(sharpe=0.21)
    d = diff_snapshots(before, after)
    assert d["risk"]["sharpe"]["flag"] is False


def test_diff_brier_regression_flagged():
    before = _snap(brier=0.28)
    after = _snap(brier=0.31)
    d = diff_snapshots(before, after)
    br = d["distribution"]["brier"]
    assert br["delta"] == pytest.approx(0.03, abs=0.001)
    assert br["flag"] is True  # 0.03 >= threshold 0.02


def test_diff_phantom_wins_increase_flagged():
    before = _snap(phantom=10)
    after = _snap(phantom=20)
    d = diff_snapshots(before, after)
    ph = d["trade_path"]["phantom_wins"]
    assert ph["delta"] == 10
    assert ph["flag"] is True  # 10 >= threshold 5


def test_diff_nested_by_style():
    before = _snap()
    after = _snap()
    after["by_style"]["position"]["win_rate"] = 55.0  # degraded from 61
    d = diff_snapshots(before, after)
    pos = d["by_style"]["position"]["win_rate"]
    assert pos["delta"] == pytest.approx(-6.0)
    assert pos["flag"] is True


def test_diff_stop_enforced_wr_flagged():
    before = _snap(stop_enforced_wr=42.0)
    after = _snap(stop_enforced_wr=38.0)
    d = diff_snapshots(before, after)
    sew = d["trade_path"]["stop_enforced_wr"]
    assert sew["delta"] == pytest.approx(-4.0)
    assert sew["flag"] is True  # 4pp >= threshold 2pp


def test_diff_missing_key_in_after():
    before = _snap()
    after = _snap()
    del after["by_month"]["2026-04"]
    # Should not crash — key exists in before but not after
    d = diff_snapshots(before, after)
    assert "2026-04" in d["by_month"]


def test_diff_extra_key_in_after():
    before = _snap()
    after = _snap()
    after["by_month"]["2026-06"] = {"n": 50, "win_rate": 65.0, "avg": 3.1, "sharpe": 1.8}
    d = diff_snapshots(before, after)
    # New month should appear
    assert "2026-06" in d["by_month"]


# ── _find_flagged helper ───────────────────────────────────────────────────────


def test_find_flagged_collects_only_flagged():
    from routers.admin import _find_flagged

    delta = {
        "returns": {
            "win_rate": {"before": 55, "after": 62, "delta": 7, "delta_pct": 12.7, "flag": True},
            "avg": {"before": 2.5, "after": 2.6, "delta": 0.1, "delta_pct": 4, "flag": False},
        },
        "risk": {
            "sharpe": {"before": 5.0, "after": 4.5, "delta": -0.5, "delta_pct": -10, "flag": True},
        },
    }
    flagged = _find_flagged(delta)
    paths = [f["metric"] for f in flagged]
    assert "returns.win_rate" in paths
    assert "risk.sharpe" in paths
    assert "returns.avg" not in paths
    assert len(flagged) == 2


def test_find_flagged_empty_delta():
    from routers.admin import _find_flagged

    assert _find_flagged({}) == []


def test_find_flagged_no_flags():
    from routers.admin import _find_flagged

    delta = {
        "returns": {
            "win_rate": {"before": 60, "after": 60.5, "delta": 0.5, "flag": False},
        }
    }
    assert _find_flagged(delta) == []
