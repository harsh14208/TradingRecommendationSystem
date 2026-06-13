"""Tests for services/execution_policy_simulator.py."""

from __future__ import annotations

import pandas as pd
import pytest

from services.execution_policy_simulator import (
    DEFAULT_POLICIES,
    PolicySummary,
    SimulationResult,
    best_policy,
    simulate_policies,
    simulate_trade,
)


def _make_ohlcv(start: str = "2026-01-01", n: int = 5) -> pd.DataFrame:
    dates = pd.date_range(start, periods=n, freq="D")
    # Provide a clear downward intraday range so limit buy fills.
    data = {
        "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "High": [101.0, 102.0, 103.0, 104.0, 105.0],
        "Low": [98.0, 99.0, 100.0, 101.0, 102.0],
        "Close": [100.0, 101.0, 102.0, 103.0, 104.0],
    }
    return pd.DataFrame(data, index=dates)


def test_simulate_trade_market_buy():
    ohlcv = _make_ohlcv()
    trade = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 103.0,
        "atr_pct": 2.0,
    }
    result = simulate_trade(trade, ohlcv, "market", friction_pct=0.50)
    assert result["policy"] == "market"
    assert result["entry_used"] == 100.0
    assert result["gross_pct"] == pytest.approx(3.0)
    assert result["net_pct"] == pytest.approx(2.5)
    assert result["filled"] is True


def test_simulate_trade_limit_buy_fills():
    ohlcv = _make_ohlcv()  # Low = 98 on signal day
    trade = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 103.0,
        "atr_pct": 2.0,
    }
    # limit price = 100 * (1 - 0.5*0.02) = 99.0; low 98 <= 99 => fill
    result = simulate_trade(trade, ohlcv, "limit", friction_pct=0.50, limit_atr_frac=0.5)
    assert result["filled"] is True
    assert result["entry_used"] == pytest.approx(99.0)
    assert result["gross_pct"] == pytest.approx((103.0 - 99.0) / 99.0 * 100.0, rel=1e-4)
    # Passive fill gets discounted friction
    assert result["friction_pct"] == pytest.approx(0.25)


def test_simulate_trade_limit_sell_fills():
    ohlcv = _make_ohlcv()
    trade = {
        "ticker": "AAPL",
        "action": "SELL",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 98.0,
        "atr_pct": 2.0,
    }
    # limit price = 100 * (1 + 0.5*0.02) = 101.0; high 101 >= 101 => fill
    result = simulate_trade(trade, ohlcv, "limit", friction_pct=0.50, limit_atr_frac=0.5)
    assert result["filled"] is True
    assert result["entry_used"] == pytest.approx(101.0)
    assert result["gross_pct"] == pytest.approx((101.0 - 98.0) / 101.0 * 100.0, rel=1e-4)


def test_simulate_trade_limit_buy_unfilled():
    ohlcv = _make_ohlcv()
    trade = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 103.0,
        "atr_pct": 10.0,  # limit price 95.0; low 98 -> no fill
    }
    # Make limit price far below low so it does not fill.
    result = simulate_trade(trade, ohlcv, "limit", friction_pct=0.50, limit_atr_frac=0.5)
    assert result["filled"] is False
    assert result["entry_used"] == 100.0  # fallback to market
    assert result["friction_pct"] == pytest.approx(0.50)


def test_simulate_trade_midpoint():
    ohlcv = _make_ohlcv()  # midpoint = (101 + 98) / 2 = 99.5
    trade = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 103.0,
        "atr_pct": 2.0,
    }
    result = simulate_trade(trade, ohlcv, "midpoint", friction_pct=0.50)
    assert result["entry_used"] == pytest.approx(99.5)
    assert result["friction_pct"] == pytest.approx(0.25)


def test_simulate_trade_next_open():
    ohlcv = _make_ohlcv()
    trade = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 103.0,
    }
    result = simulate_trade(trade, ohlcv, "next_open", friction_pct=0.50)
    assert result["entry_used"] == pytest.approx(101.0)


def test_simulate_trade_next_close():
    ohlcv = _make_ohlcv()
    trade = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_date": "2026-01-01",
        "entry_price": 100.0,
        "exit_price": 103.0,
    }
    result = simulate_trade(trade, ohlcv, "next_close", friction_pct=0.50)
    assert result["entry_used"] == pytest.approx(101.0)


def test_simulate_policies_summary():
    ohlcv = _make_ohlcv()
    trades = [
        {
            "ticker": "AAPL",
            "action": "BUY",
            "entry_date": "2026-01-01",
            "entry_price": 100.0,
            "exit_price": 103.0,
            "atr_pct": 2.0,
            "hold_days": 3,
        },
        {
            "ticker": "AAPL",
            "action": "BUY",
            "entry_date": "2026-01-02",
            "entry_price": 101.0,
            "exit_price": 100.0,
            "atr_pct": 2.0,
            "hold_days": 1,
        },
    ]
    result = simulate_policies(
        trades,
        {"AAPL": ohlcv},
        friction_pct=0.50,
    )
    assert len(result.summaries) == len(DEFAULT_POLICIES)
    policies = {s.policy for s in result.summaries}
    assert policies == set(DEFAULT_POLICIES)
    # Every summary should have at least one trade
    assert all(s.n_total == 2 for s in result.summaries)
    # Limit should fill for the first trade (low well below limit price)
    limit_summary = next(s for s in result.summaries if s.policy == "limit")
    assert limit_summary.n_filled >= 1


def test_best_policy():
    summaries = [
        PolicySummary(
            policy="market",
            n_total=10,
            n_filled=10,
            fill_rate=1.0,
            avg_gross_bps=100.0,
            avg_net_bps=50.0,
            win_rate=0.5,
            gross_sharpe_annual=None,
            net_sharpe_annual=None,
            avg_entry_slippage_bps=0.0,
        ),
        PolicySummary(
            policy="limit",
            n_total=10,
            n_filled=8,
            fill_rate=0.8,
            avg_gross_bps=120.0,
            avg_net_bps=80.0,
            win_rate=0.6,
            gross_sharpe_annual=None,
            net_sharpe_annual=None,
            avg_entry_slippage_bps=-10.0,
        ),
    ]
    result = SimulationResult(summaries=summaries)
    best = best_policy(result)
    assert best is not None
    assert best.policy == "limit"


def test_empty_result_best_policy_returns_none():
    assert best_policy(SimulationResult()) is None
