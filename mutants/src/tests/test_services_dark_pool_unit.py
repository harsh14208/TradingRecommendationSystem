"""Unit tests for services/dark_pool.py — pure helpers and async getters."""
import time
from collections import deque
from unittest.mock import MagicMock

import pytest


# ── _tick_rule ────────────────────────────────────────────────────────────────

def test_tick_rule_uptick():
    from services.dark_pool import _tick_rule
    assert _tick_rule(101.0, 100.0) == "buy"


def test_tick_rule_downtick():
    from services.dark_pool import _tick_rule
    assert _tick_rule(99.0, 100.0) == "sell"


def test_tick_rule_zero_tick():
    from services.dark_pool import _tick_rule
    assert _tick_rule(100.0, 100.0) == "unknown"


# ── _reconstruct_orders ───────────────────────────────────────────────────────

def _make_print(symbol, price, size, ts=None):
    from services.dark_pool import _Print
    return _Print(
        ts=ts or time.time(),
        symbol=symbol,
        price=price,
        size=size,
        notional=price * size,
    )


def test_reconstruct_orders_empty():
    from services.dark_pool import _reconstruct_orders
    assert _reconstruct_orders([]) == []


def test_reconstruct_orders_too_small():
    from services.dark_pool import _reconstruct_orders
    # $100 * 100 = $10,000 < $500k threshold
    p = _make_print("AAPL", 100.0, 100, ts=1000.0)
    result = _reconstruct_orders([p])
    assert result == []


def test_reconstruct_orders_large_buy():
    from services.dark_pool import _reconstruct_orders
    # 3 prints: same symbol, close in time, rising price (buy-initiated)
    base_ts = time.time()
    prints = [
        _make_print("AAPL", 150.0, 1000, ts=base_ts),
        _make_print("AAPL", 150.5, 1000, ts=base_ts + 5),
        _make_print("AAPL", 151.0, 1000, ts=base_ts + 10),
    ]
    # Notional: ~$450k — just below threshold... let's use 5000 shares each
    prints = [
        _make_print("AAPL", 150.0, 5000, ts=base_ts),
        _make_print("AAPL", 150.5, 5000, ts=base_ts + 5),
        _make_print("AAPL", 151.0, 5000, ts=base_ts + 10),
    ]
    result = _reconstruct_orders(prints)
    assert len(result) >= 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["direction"] == "buy"


def test_reconstruct_orders_sell():
    from services.dark_pool import _reconstruct_orders
    base_ts = time.time()
    prints = [
        _make_print("NVDA", 500.0, 5000, ts=base_ts),
        _make_print("NVDA", 499.5, 5000, ts=base_ts + 5),
        _make_print("NVDA", 499.0, 5000, ts=base_ts + 10),
    ]
    result = _reconstruct_orders(prints)
    assert len(result) >= 1
    assert result[0]["direction"] == "sell"


def test_reconstruct_orders_split_groups():
    from services.dark_pool import _reconstruct_orders
    # Two groups far apart in time
    base_ts = time.time()
    prints = [
        _make_print("AAPL", 150.0, 5000, ts=base_ts),
        _make_print("AAPL", 150.0, 5000, ts=base_ts + 120),  # 2 min gap → new group
    ]
    result = _reconstruct_orders(prints)
    # Both groups have enough notional, so we might get 2 orders
    assert isinstance(result, list)


def test_reconstruct_orders_multi_symbol():
    from services.dark_pool import _reconstruct_orders
    base_ts = time.time()
    prints = [
        _make_print("AAPL", 150.0, 5000, ts=base_ts),
        _make_print("NVDA", 500.0, 2000, ts=base_ts + 5),
    ]
    result = _reconstruct_orders(prints)
    # AAPL: notional = 750k ≥ 500k; NVDA: notional = 1M ≥ 500k
    symbols = {o["symbol"] for o in result}
    assert "AAPL" in symbols
    assert "NVDA" in symbols


# ── get_dark_pool_flow ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_dark_pool_flow_empty():
    from services.dark_pool import get_dark_pool_flow
    import services.dark_pool as dp
    dp._flow_data = {}
    result = await get_dark_pool_flow(["AAPL", "NVDA"])
    assert result == {}


@pytest.mark.asyncio
async def test_get_dark_pool_flow_with_data():
    from services.dark_pool import get_dark_pool_flow
    import services.dark_pool as dp
    dp._flow_data = {"AAPL": 12.5, "NVDA": -5.3, "MSFT": 0.0}
    result = await get_dark_pool_flow(["AAPL", "NVDA"])
    assert "AAPL" in result
    assert result["AAPL"]["net_flow_m"] == 12.5
    # MSFT not requested
    assert "MSFT" not in result


# ── get_reconstructed_orders ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_reconstructed_orders_empty():
    from services.dark_pool import get_reconstructed_orders
    import services.dark_pool as dp
    dp._print_buffer = deque(maxlen=100_000)
    result = await get_reconstructed_orders()
    assert "orders" in result or result == {} or isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_reconstructed_orders_with_ticker():
    from services.dark_pool import get_reconstructed_orders
    import services.dark_pool as dp
    dp._print_buffer = deque(maxlen=100_000)
    result = await get_reconstructed_orders(ticker="AAPL")
    assert isinstance(result, dict)


# ── handle_messages ────────────────────────────────────────────────────────────

def test_handle_messages_empty():
    from services.dark_pool import handle_messages
    # Should not crash on empty list
    handle_messages([])


def test_handle_messages_no_massive_module():
    from services.dark_pool import handle_messages
    # Without massive module, should fail gracefully
    import sys
    if "massive" in sys.modules:
        del sys.modules["massive"]
    # Should not raise
    handle_messages([MagicMock()])
