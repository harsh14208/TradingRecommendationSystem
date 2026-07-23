"""
Real-time tick streaming from Alpaca Markets (free IEX feed).
Includes a 15-second heartbeat watchdog: if no frames are received in 15s,
the connection is forcefully torn down and reconnected with exponential backoff.
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Optional

log = logging.getLogger(__name__)

_task: Optional[asyncio.Task] = None
_price_cache: dict[str, float] = {}
_subscribed: set[str] = set()

_WS_URL = "wss://stream.data.alpaca.markets/v2/iex"
_HEARTBEAT_SEC = 45  # watchdog fires if no frame in this window
# IEX can be quiet for 30–40s between trades; 15s was far too aggressive.
_MAX_RECONNECT_LOGS_PER_HOUR = 3  # rate-limit reconnect noise in logs
_reconnect_log_count: int = 0
_reconnect_log_window: float = 0.0


def _should_log_reconnect() -> bool:
    """Rate-limit reconnect logs to _MAX_RECONNECT_LOGS_PER_HOUR per hour."""
    global _reconnect_log_count, _reconnect_log_window
    now = time.monotonic()
    if now - _reconnect_log_window > 3600:
        _reconnect_log_window = now
        _reconnect_log_count = 0
    _reconnect_log_count += 1
    return _reconnect_log_count <= _MAX_RECONNECT_LOGS_PER_HOUR


async def _run(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning("websockets not installed — Alpaca stream disabled")
            return

    global _subscribed
    _subscribed = set(tickers)
    backoff = 1

    while True:
        _last_frame = time.monotonic()

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    if _should_log_reconnect():
                        log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info("Alpaca WS: authenticated — %d tickers", len(tickers))

                if tickers:
                    await ws.send(json.dumps({"action": "subscribe", "trades": tickers}))

                watchdog_task = asyncio.create_task(_watchdog(ws))
                try:
                    async for raw in ws:
                        _last_frame = time.monotonic()
                        msgs = json.loads(raw)
                        for m in msgs:
                            if m.get("T") != "t":
                                continue
                            ticker = m["S"]
                            price = float(m["p"])
                            _price_cache[ticker] = price
                            try:
                                from services.alpaca_rest import record_price

                                record_price(ticker, price)
                            except ImportError:
                                pass
                            try:
                                await broadcast_fn(
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            if _should_log_reconnect():
                log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


def start(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def stop() -> None:
    global _task
    if _task and not _task.done():
        _task.cancel()


def get_price(ticker: str) -> Optional[float]:
    return _price_cache.get(ticker)
