"""Smoke tests for the research backtest harnesses."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

BACKEND = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


@pytest.fixture
def sample_trades_csv(tmp_path: Path) -> Path:
    """Minimal trade ledger sufficient for both harnesses."""
    rows = []
    base_date = pd.Timestamp("2020-01-01")
    for i in range(40):
        rows.append(
            {
                "date": (base_date + pd.Timedelta(days=i * 5)).strftime("%Y-%m-%d"),
                "ticker": f"TICK{i % 5}",
                "action": "BUY",
                "score": 50.0,
                "entry": 100.0,
                "stop": 95.0,
                "target": 105.0,
                "exit_price": 101.0,
                "exit_reason": "target",
                "exit_day": 2,
                "gross_pct": 1.0,
                "net_pct": 0.8 if i % 3 != 0 else -0.5,
                "net_pct_alt": 0.8,
                "spy_leg_pct": 0.0,
                "size_mult": 1.0,
                "overnight_pct": 0.0,
                "intraday_pct": 0.8,
                "entry_style": "open",
                "mr_trigger": "multi",
                "max21": 2.0 + (i % 5) * 0.5,
                "quality_score": 50.0,
                "sector_etf": "XLC" if i % 2 == 0 else "XLF",
                "hmm_bull_prob": 0.7 if i % 4 == 0 else 0.3,
                "hmm_trans_risk": 0.02,
            }
        )
    df = pd.DataFrame(rows)
    path = tmp_path / "trades.csv"
    df.to_csv(path, index=False)
    return path


class TestRegimeCohortHarness:
    def test_runs_without_error(self, sample_trades_csv: Path, tmp_path: Path) -> None:
        out = tmp_path / "regime.csv"
        result = subprocess.run(
            [
                PYTHON,
                str(BACKEND / "scripts" / "backtest_regime_cohort.py"),
                "--trades",
                str(sample_trades_csv),
                "--output",
                str(out),
                "--strategy",
                "filter",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stderr
        assert "Baseline" in result.stdout
        assert out.exists()


class TestMaxEffectHarness:
    def test_runs_without_error(self, sample_trades_csv: Path, tmp_path: Path) -> None:
        out = tmp_path / "max.csv"
        result = subprocess.run(
            [
                PYTHON,
                str(BACKEND / "scripts" / "backtest_max_effect.py"),
                "--trades",
                str(sample_trades_csv),
                "--output",
                str(out),
                "--strategy",
                "filter_bottom",
                "--threshold",
                "0.5",
            ],
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stderr
        assert "Baseline" in result.stdout
        assert out.exists()
