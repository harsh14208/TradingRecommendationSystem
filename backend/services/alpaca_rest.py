"""
Async client for Alpaca Markets paper trading REST API.
Same ALPACA_API_KEY / ALPACA_API_SECRET used for the tick stream work here too.
Paper base URL is separate from the live/data URL.

Includes slippage protection: if the current price has moved more than
SLIPPAGE_THRESHOLD ($0.05) from the signal price within SLIPPAGE_WINDOW_MS (100ms),
the order is rejected to prevent bad fills.
"""

import ssl
import time
from typing import Any, Optional

import aiohttp
import certifi

PAPER_BASE = "https://paper-api.alpaca.markets"

# Slippage protection configuration
SLIPPAGE_THRESHOLD = 0.05  # $0.05 max price movement
SLIPPAGE_WINDOW_MS = 100  # 100ms lookback window


def _headers(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=certifi.where())
    return ctx


async def get_account(api_key: str, api_secret: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{PAPER_BASE}/v2/account",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def get_positions(api_key: str, api_secret: str) -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{PAPER_BASE}/v2/positions",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def get_orders(api_key: str, api_secret: str, status: str = "all", limit: int = 50) -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{PAPER_BASE}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


# Price history for slippage detection: {ticker: [(timestamp_ms, price), ...]}
_price_history: dict[str, list[tuple[float, float]]] = {}


def record_price(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def check_slippage(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


async def place_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
) -> dict:
    """
    Place an order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{PAPER_BASE}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def close_position(api_key: str, api_secret: str, symbol: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.delete(
            f"{PAPER_BASE}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def cancel_order(api_key: str, api_secret: str, order_id: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.delete(
            f"{PAPER_BASE}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()
