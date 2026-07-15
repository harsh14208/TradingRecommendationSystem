"""Unit tests for the residual cash overlay and drawdown throttle in services/portfolio_allocator."""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services import portfolio_allocator as pa


@pytest.fixture(autouse=True)
def _enable_overlay(monkeypatch):
    """Enable cash overlay with deterministic defaults for every test."""
    monkeypatch.setattr(pa, "_CASH_OVERLAY_ENABLE", True)
    monkeypatch.setattr(pa, "_CASH_OVERLAY_TICKER", "SGOV")
    monkeypatch.setattr(pa, "_CASH_OVERLAY_BETA_TICKER", "VOO")
    monkeypatch.setattr(pa, "_CASH_OVERLAY_MAX_FRACTION", 0.50)
    monkeypatch.setattr(pa, "_CASH_OVERLAY_VIX_THRESHOLD", 22.0)
    monkeypatch.setattr(pa, "_CASH_OVERLAY_MIN_TRADE_DOLLARS", 100.0)


def _mock_vix(value: float | None):
    """Return a patcher for _latest_vix that returns the given value."""
    return patch.object(pa, "_latest_vix", new=AsyncMock(return_value=value))


@pytest.mark.asyncio
async def test_overlay_disabled_does_nothing():
    pa._CASH_OVERLAY_ENABLE = False
    orders = await pa._add_overlay_orders(
        orders=[],
        final_weights={"AAPL": 0.20},
        current_weights={},
        total_cash=100_000.0,
        dd_mult=1.0,
    )
    assert orders == []


@pytest.mark.asyncio
async def test_residual_cash_buys_parking_ticker():
    with _mock_vix(25.0):  # high VIX -> parking
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"AAPL": 0.20},
            current_weights={},
            total_cash=100_000.0,
            dd_mult=1.0,
        )
    assert len(orders) == 1
    assert orders[0]["ticker"] == "SGOV"
    assert orders[0]["action"] == "BUY"
    assert orders[0]["notional"] == pytest.approx(50_000.0, abs=1.0)


@pytest.mark.asyncio
async def test_low_vix_buys_beta_ticker():
    with _mock_vix(18.0):  # low VIX -> beta sleeve
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"AAPL": 0.20},
            current_weights={},
            total_cash=100_000.0,
            dd_mult=1.0,
        )
    assert len(orders) == 1
    assert orders[0]["ticker"] == "VOO"
    assert orders[0]["action"] == "BUY"


@pytest.mark.asyncio
async def test_drawdown_throttle_uses_parking_even_with_low_vix():
    with _mock_vix(18.0):
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"AAPL": 0.10},
            current_weights={},
            total_cash=100_000.0,
            dd_mult=0.5,  # throttle active
        )
    assert len(orders) == 1
    assert orders[0]["ticker"] == "SGOV"


@pytest.mark.asyncio
async def test_existing_overlay_position_is_rebalanced():
    with _mock_vix(25.0):
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"AAPL": 0.20},
            current_weights={"SGOV": 0.60},  # overweight vs 0.50 cap
            total_cash=100_000.0,
            dd_mult=1.0,
        )
    sgov_orders = [o for o in orders if o["ticker"] == "SGOV"]
    assert len(sgov_orders) == 1
    assert sgov_orders[0]["action"] == "SELL"
    assert sgov_orders[0]["notional"] == pytest.approx(10_000.0, abs=1.0)


@pytest.mark.asyncio
async def test_switch_from_parking_to_beta_closes_parking():
    with _mock_vix(18.0):
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"AAPL": 0.20},
            current_weights={"SGOV": 0.30},
            total_cash=100_000.0,
            dd_mult=1.0,
        )
    tickers = [o["ticker"] for o in orders]
    assert "SGOV" in tickers
    assert "VOO" in tickers
    sgov = next(o for o in orders if o["ticker"] == "SGOV")
    voo = next(o for o in orders if o["ticker"] == "VOO")
    assert sgov["action"] == "SELL"
    assert voo["action"] == "BUY"


@pytest.mark.asyncio
async def test_overlay_skipped_when_engine_manages_same_ticker():
    with _mock_vix(18.0):
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"VOO": 0.20, "AAPL": 0.10},
            current_weights={},
            total_cash=100_000.0,
            dd_mult=1.0,
        )
    assert not any(o["ticker"] == "VOO" and o["signal_id"] is None for o in orders)


@pytest.mark.asyncio
async def test_small_residual_below_min_trade_is_ignored():
    with _mock_vix(25.0):
        orders = await pa._add_overlay_orders(
            orders=[],
            final_weights={"AAPL": 0.99},
            current_weights={},
            total_cash=10_000.0,
            dd_mult=1.0,
        )
    assert orders == []


def test_compute_dd_multiplier_default(monkeypatch):
    """R7: no throttle below trigger; throttle multiplier above trigger."""
    monkeypatch.setattr(pa, "_DD_THROTTLE_TRIGGER_PCT", 3.0)
    monkeypatch.setattr(pa, "_DD_THROTTLE_MULT", 0.5)
    assert pa.compute_dd_multiplier(0.0) == 1.0
    assert pa.compute_dd_multiplier(2.99) == 1.0
    assert pa.compute_dd_multiplier(3.0) == 1.0
    assert pa.compute_dd_multiplier(3.01) == 0.5
    assert pa.compute_dd_multiplier(8.0) == 0.5


def test_compute_dd_multiplier_env_overrides(monkeypatch):
    """R7: env vars can tune the throttle trigger and multiplier."""
    monkeypatch.setattr(pa, "_DD_THROTTLE_TRIGGER_PCT", 5.0)
    monkeypatch.setattr(pa, "_DD_THROTTLE_MULT", 0.25)
    assert pa.compute_dd_multiplier(4.9) == 1.0
    assert pa.compute_dd_multiplier(5.1) == 0.25
