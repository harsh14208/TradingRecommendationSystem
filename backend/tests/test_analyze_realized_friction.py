"""Tests for scripts/analyze_realized_friction.py."""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.analyze_realized_friction import _compute_metrics, _summarize


def test_compute_metrics() -> None:
    df = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL"],
            "qty": [100.0, 50.0],
            "price": [200.0, 210.0],
            "commission": [10.0, 5.0],
            "fees": [0.0, 1.0],
            "slippage_bps": [5.0, -2.0],
        }
    )
    out = _compute_metrics(df)
    assert out["commission_bps"].iloc[0] == pytest.approx(5.0, rel=1e-3)  # 10 / (100*200) * 1e4
    assert out["total_cost_bps"].iloc[0] == pytest.approx(5.0 + 5.0, rel=1e-3)


def test_summarize_round_trip() -> None:
    df = pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT"],
            "slippage_bps": [10.0, 20.0],
            "commission_bps": [5.0, 5.0],
            "fees_bps": [0.0, 0.0],
            "total_cost_bps": [15.0, 25.0],
        }
    )
    summary = _summarize(df)
    assert summary.n_fills == 2
    assert summary.n_tickers == 2
    assert summary.mean_slippage_bps == pytest.approx(15.0)
    assert summary.mean_round_trip_bps == pytest.approx(40.0)  # 2 * (15+25)/2
