"""Smoke tests for the cross-sectional alt-data attribution helpers."""

from __future__ import annotations

import numpy as np
import pytest

from scripts import analyze_cross_sectional_alt_data as ana


def test_epoch_sharpe_groups_folds_by_year() -> None:
    """epoch_sharpe should aggregate only folds inside each epoch window."""
    folds = [
        {"fold_year": 2012, "gross": np.array([0.01, 0.02]), "turnover": np.array([0.1, 0.1])},
        {"fold_year": 2019, "gross": np.array([0.03]), "turnover": np.array([0.1])},
        {"fold_year": 2025, "gross": np.array([0.04]), "turnover": np.array([0.1])},
    ]
    epochs = [("pre_2019", 2012, 2018), ("2019_2024", 2019, 2024), ("post_2024", 2025, None)]
    out = ana.epoch_sharpe(folds, epochs, cost_bps=0.0)
    assert out["pre_2019"]["n_folds"] == 1
    assert out["2019_2024"]["n_folds"] == 1
    assert out["post_2024"]["n_folds"] == 1
    # With zero costs, net = gross.
    np.testing.assert_allclose(out["pre_2019"]["ann_ret_net"], np.mean([0.01, 0.02]) * ana.csam.PERIODS_PER_YEAR)


def test_paired_bootstrap_returns_reasonable_distribution() -> None:
    """When treatment is identical to baseline, ΔSharpe distribution should center near 0."""
    net = np.array([0.01, -0.005, 0.02, -0.01, 0.015, -0.002, 0.008, -0.008])
    base_folds = [{"net": net[:4], "sharpe_net": 0.1}, {"net": net[4:], "sharpe_net": 0.1}]
    treat_folds = [{"net": net[:4], "sharpe_net": 0.1}, {"net": net[4:], "sharpe_net": 0.1}]
    bs = ana.paired_bootstrap(base_folds, treat_folds, n_boot=500, block=2, seed=7)
    assert "obs_delta_sharpe" in bs
    assert bs["obs_delta_sharpe"] == pytest.approx(0.0, abs=1e-9)
    # CI should include 0.
    assert bs["q05_delta_sharpe"] <= 0.0 <= bs["q95_delta_sharpe"]
    # Under H0 the two-sided p should be large.  With identical series all
    # bootstrap ΔSharpes are exactly 0, so the one-sided p is 1.0; with noisy
    # identical series it is ~0.5.
    assert bs["p_value_two_sided"] > 0.5
    assert bs["p_value_one_sided"] >= 0.3


def test_paired_bootstrap_detects_positive_shift() -> None:
    """A consistently positive treatment shift should yield a positive ΔSharpe CI."""
    rng = np.random.default_rng(9)
    base = rng.normal(0.0, 0.02, size=64)
    treat = base + 0.05  # pure positive shift
    base_folds = [{"net": base[:32], "sharpe_net": 0.0}, {"net": base[32:], "sharpe_net": 0.0}]
    treat_folds = [{"net": treat[:32], "sharpe_net": 1.0}, {"net": treat[32:], "sharpe_net": 1.0}]
    bs = ana.paired_bootstrap(base_folds, treat_folds, n_boot=500, block=4, seed=8)
    assert bs["obs_delta_sharpe"] > 1.0
    assert bs["q05_delta_sharpe"] > 0.0
    assert bs["p_value_two_sided"] < 0.05
    assert bs["p_value_one_sided"] < 0.05


import pandas as pd


def test_gdelt_cross_sectional_merge_pit_lag() -> None:
    """GDELT tone panel is lagged +1 day before merge_asof into the research panel."""
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]),
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "close": [100.0, 101.0, 102.0],
        }
    )
    gdelt = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "ticker": ["AAPL", "AAPL"],
            "tone_z": [-1.5, -1.2],
            "tone_mean": [-2.0, -1.8],
        }
    )
    # Apply the same transformation as cross_sectional_alpha_model.py build_panel.
    gdelt = gdelt.assign(date=gdelt["date"] + pd.Timedelta(days=1))
    merged = pd.merge_asof(
        panel.sort_values("date"),
        gdelt[["date", "ticker", "tone_z", "tone_mean"]].sort_values("date"),
        on="date",
        by="ticker",
        direction="backward",
    )
    # 2024-01-03 signal uses 2024-01-02 tone (lagged +1 day).
    assert merged.loc[0, "tone_z"] == pytest.approx(-1.5)
    assert merged.loc[1, "tone_z"] == pytest.approx(-1.2)
    assert merged.loc[2, "tone_z"] == pytest.approx(-1.2)
