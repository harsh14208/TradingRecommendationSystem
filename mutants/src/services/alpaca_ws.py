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
_HEARTBEAT_SEC = 15  # watchdog fires if no frame in this window


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__run__mutmut)
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_orig(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_1(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning(None)
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_2(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning("XXwebsockets not installed — Alpaca stream disabledXX")
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_3(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning("websockets not installed — alpaca stream disabled")
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_4(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning("WEBSOCKETS NOT INSTALLED — ALPACA STREAM DISABLED")
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_5(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning("websockets not installed — Alpaca stream disabled")
            return

    global _subscribed
    _subscribed = None
    backoff = 1

    while True:
        _last_frame = time.monotonic()

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_6(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        try:
            from websockets import connect  # type: ignore[no-redef]
        except ImportError:
            log.warning("websockets not installed — Alpaca stream disabled")
            return

    global _subscribed
    _subscribed = set(None)
    backoff = 1

    while True:
        _last_frame = time.monotonic()

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_7(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
    backoff = None

    while True:
        _last_frame = time.monotonic()

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_8(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
    backoff = 2

    while True:
        _last_frame = time.monotonic()

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_9(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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

    while False:
        _last_frame = time.monotonic()

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_10(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
        _last_frame = None

        async def _watchdog(ws):  # noqa: B023 — intentional nonlocal capture
            """Cancel the connection if no frame arrives within _HEARTBEAT_SEC."""
            nonlocal _last_frame
            while True:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_11(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
            while False:
                await asyncio.sleep(5)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_12(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                await asyncio.sleep(None)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_13(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                await asyncio.sleep(6)
                if time.monotonic() - _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_14(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                if time.monotonic() + _last_frame > _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_15(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                if time.monotonic() - _last_frame >= _HEARTBEAT_SEC:  # noqa: B023
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_16(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning(None, _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_17(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", None)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_18(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning(_HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_19(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", )
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_20(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("XXAlpaca WS: no frame in %ds — forcing reconnectXX", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_21(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("alpaca ws: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_22(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("ALPACA WS: NO FRAME IN %DS — FORCING RECONNECT", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_23(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(None, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_24(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=None, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_25(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=None) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_26(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_27(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_28(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_29(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=21, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_30(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=11) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_31(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = None  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_32(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 2  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_33(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = None
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_34(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = None
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_35(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = None
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_36(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(None)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_37(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_38(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(None):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_39(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get(None) == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_40(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("XXTXX") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_41(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("t") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_42(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") != "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_43(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "XXconnectedXX" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_44(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "CONNECTED" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_45(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning(None, msgs)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_46(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", None)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_47(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning(msgs)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_48(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", )

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_49(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("XXAlpaca WS unexpected greeting: %sXX", msgs)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_50(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("alpaca ws unexpected greeting: %s", msgs)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_51(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("ALPACA WS UNEXPECTED GREETING: %S", msgs)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_52(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_53(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps(None))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_54(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"XXactionXX": "auth", "key": api_key, "secret": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_55(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"ACTION": "auth", "key": api_key, "secret": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_56(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "XXauthXX", "key": api_key, "secret": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_57(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "AUTH", "key": api_key, "secret": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_58(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "XXkeyXX": api_key, "secret": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_59(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "KEY": api_key, "secret": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_60(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "XXsecretXX": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_61(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "SECRET": api_secret}))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_62(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_63(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_64(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_65(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_66(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_67(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(None):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_68(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" or m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_69(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get(None) == "success" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_70(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("XXTXX") == "success" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_71(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("t") == "success" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_72(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") != "success" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_73(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "XXsuccessXX" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_74(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "SUCCESS" and m.get("msg") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_75(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get(None) == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_76(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("XXmsgXX") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_77(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("MSG") == "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_78(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") != "authenticated" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_79(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "XXauthenticatedXX" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_80(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "AUTHENTICATED" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_81(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning(None, msgs)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_82(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_83(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning(msgs)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_84(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", )
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_85(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("XXAlpaca auth failed: %sXX", msgs)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_86(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("alpaca auth failed: %s", msgs)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_87(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("ALPACA AUTH FAILED: %S", msgs)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_88(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info(None, len(tickers))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_89(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info("Alpaca WS: authenticated — %d tickers", None)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_90(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info(len(tickers))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_91(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info("Alpaca WS: authenticated — %d tickers", )

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_92(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info("XXAlpaca WS: authenticated — %d tickersXX", len(tickers))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_93(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info("alpaca ws: authenticated — %d tickers", len(tickers))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_94(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
                    log.warning("Alpaca WS unexpected greeting: %s", msgs)

                await ws.send(json.dumps({"action": "auth", "key": api_key, "secret": api_secret}))
                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
                    log.warning("Alpaca auth failed: %s", msgs)
                    return
                log.info("ALPACA WS: AUTHENTICATED — %D TICKERS", len(tickers))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_95(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(None)

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_96(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps(None))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_97(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps({"XXactionXX": "subscribe", "trades": tickers}))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_98(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps({"ACTION": "subscribe", "trades": tickers}))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_99(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps({"action": "XXsubscribeXX", "trades": tickers}))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_100(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps({"action": "SUBSCRIBE", "trades": tickers}))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_101(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps({"action": "subscribe", "XXtradesXX": tickers}))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_102(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                    await ws.send(json.dumps({"action": "subscribe", "TRADES": tickers}))

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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_103(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                watchdog_task = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_104(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                watchdog_task = asyncio.create_task(None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_105(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                watchdog_task = asyncio.create_task(_watchdog(None))
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_106(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                        _last_frame = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_107(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                        msgs = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_108(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                        msgs = json.loads(None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_109(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            if m.get(None) != "t":
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_110(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            if m.get("XXTXX") != "t":
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_111(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            if m.get("t") != "t":
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_112(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            if m.get("T") == "t":
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_113(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            if m.get("T") != "XXtXX":
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_114(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            if m.get("T") != "T":
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_115(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                break
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_116(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            ticker = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_117(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            ticker = m["XXSXX"]
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_118(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            ticker = m["s"]
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_119(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            price = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_120(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            price = float(None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_121(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            price = float(m["XXpXX"])
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_122(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            price = float(m["P"])
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_123(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                            _price_cache[ticker] = None
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_124(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                                record_price(None, price)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_125(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                                record_price(ticker, None)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_126(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                                record_price(price)
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_127(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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

                                record_price(ticker, )
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_128(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    None
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_129(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"XXtypeXX": "tick", "ticker": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_130(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"TYPE": "tick", "ticker": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_131(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "XXtickXX", "ticker": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_132(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "TICK", "ticker": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_133(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "XXtickerXX": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_134(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "TICKER": ticker, "price": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_135(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "XXpriceXX": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_136(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "PRICE": price, "size": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_137(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "XXsizeXX": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_138(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "SIZE": m.get("s", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_139(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get(None, 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_140(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get("s", None)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_141(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get(0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_142(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get("s", )}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_143(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get("XXsXX", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_144(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get("S", 0)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_145(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
                                    {"type": "tick", "ticker": ticker, "price": price, "size": m.get("s", 1)}
                                )
                            except Exception:
                                pass
                finally:
                    watchdog_task.cancel()

        except asyncio.CancelledError:
            log.info("Alpaca WS task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_146(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.info(None)
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_147(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.info("XXAlpaca WS task cancelledXX")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_148(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.info("alpaca ws task cancelled")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_149(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.info("ALPACA WS TASK CANCELLED")
            return
        except Exception as e:
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_150(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning(None, e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_151(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", None, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_152(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, None)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_153(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning(e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_154(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_155(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, )
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_156(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("XXAlpaca WS error: %s — reconnecting in %dsXX", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_157(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("alpaca ws error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_158(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("ALPACA WS ERROR: %S — RECONNECTING IN %DS", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_159(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(None)
            backoff = min(backoff * 2, 60)


async def x__run__mutmut_160(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = None


async def x__run__mutmut_161(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(None, 60)


async def x__run__mutmut_162(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, None)


async def x__run__mutmut_163(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(60)


async def x__run__mutmut_164(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, )


async def x__run__mutmut_165(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff / 2, 60)


async def x__run__mutmut_166(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 3, 60)


async def x__run__mutmut_167(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable):
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
                    log.warning("Alpaca WS: no frame in %ds — forcing reconnect", _HEARTBEAT_SEC)
                    await ws.close()
                    return

        try:
            async with connect(_WS_URL, ping_interval=20, ping_timeout=10) as ws:
                backoff = 1  # reset on clean connect

                raw = await ws.recv()
                _last_frame = time.monotonic()
                msgs = json.loads(raw)
                if not any(m.get("T") == "connected" for m in msgs):
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
            log.warning("Alpaca WS error: %s — reconnecting in %ds", e, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 61)

mutants_x__run__mutmut['_mutmut_orig'] = x__run__mutmut_orig # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_1'] = x__run__mutmut_1 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_2'] = x__run__mutmut_2 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_3'] = x__run__mutmut_3 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_4'] = x__run__mutmut_4 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_5'] = x__run__mutmut_5 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_6'] = x__run__mutmut_6 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_7'] = x__run__mutmut_7 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_8'] = x__run__mutmut_8 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_9'] = x__run__mutmut_9 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_10'] = x__run__mutmut_10 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_11'] = x__run__mutmut_11 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_12'] = x__run__mutmut_12 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_13'] = x__run__mutmut_13 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_14'] = x__run__mutmut_14 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_15'] = x__run__mutmut_15 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_16'] = x__run__mutmut_16 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_17'] = x__run__mutmut_17 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_18'] = x__run__mutmut_18 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_19'] = x__run__mutmut_19 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_20'] = x__run__mutmut_20 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_21'] = x__run__mutmut_21 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_22'] = x__run__mutmut_22 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_23'] = x__run__mutmut_23 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_24'] = x__run__mutmut_24 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_25'] = x__run__mutmut_25 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_26'] = x__run__mutmut_26 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_27'] = x__run__mutmut_27 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_28'] = x__run__mutmut_28 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_29'] = x__run__mutmut_29 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_30'] = x__run__mutmut_30 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_31'] = x__run__mutmut_31 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_32'] = x__run__mutmut_32 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_33'] = x__run__mutmut_33 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_34'] = x__run__mutmut_34 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_35'] = x__run__mutmut_35 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_36'] = x__run__mutmut_36 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_37'] = x__run__mutmut_37 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_38'] = x__run__mutmut_38 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_39'] = x__run__mutmut_39 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_40'] = x__run__mutmut_40 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_41'] = x__run__mutmut_41 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_42'] = x__run__mutmut_42 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_43'] = x__run__mutmut_43 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_44'] = x__run__mutmut_44 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_45'] = x__run__mutmut_45 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_46'] = x__run__mutmut_46 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_47'] = x__run__mutmut_47 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_48'] = x__run__mutmut_48 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_49'] = x__run__mutmut_49 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_50'] = x__run__mutmut_50 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_51'] = x__run__mutmut_51 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_52'] = x__run__mutmut_52 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_53'] = x__run__mutmut_53 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_54'] = x__run__mutmut_54 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_55'] = x__run__mutmut_55 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_56'] = x__run__mutmut_56 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_57'] = x__run__mutmut_57 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_58'] = x__run__mutmut_58 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_59'] = x__run__mutmut_59 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_60'] = x__run__mutmut_60 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_61'] = x__run__mutmut_61 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_62'] = x__run__mutmut_62 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_63'] = x__run__mutmut_63 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_64'] = x__run__mutmut_64 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_65'] = x__run__mutmut_65 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_66'] = x__run__mutmut_66 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_67'] = x__run__mutmut_67 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_68'] = x__run__mutmut_68 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_69'] = x__run__mutmut_69 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_70'] = x__run__mutmut_70 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_71'] = x__run__mutmut_71 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_72'] = x__run__mutmut_72 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_73'] = x__run__mutmut_73 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_74'] = x__run__mutmut_74 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_75'] = x__run__mutmut_75 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_76'] = x__run__mutmut_76 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_77'] = x__run__mutmut_77 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_78'] = x__run__mutmut_78 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_79'] = x__run__mutmut_79 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_80'] = x__run__mutmut_80 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_81'] = x__run__mutmut_81 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_82'] = x__run__mutmut_82 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_83'] = x__run__mutmut_83 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_84'] = x__run__mutmut_84 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_85'] = x__run__mutmut_85 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_86'] = x__run__mutmut_86 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_87'] = x__run__mutmut_87 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_88'] = x__run__mutmut_88 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_89'] = x__run__mutmut_89 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_90'] = x__run__mutmut_90 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_91'] = x__run__mutmut_91 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_92'] = x__run__mutmut_92 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_93'] = x__run__mutmut_93 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_94'] = x__run__mutmut_94 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_95'] = x__run__mutmut_95 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_96'] = x__run__mutmut_96 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_97'] = x__run__mutmut_97 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_98'] = x__run__mutmut_98 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_99'] = x__run__mutmut_99 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_100'] = x__run__mutmut_100 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_101'] = x__run__mutmut_101 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_102'] = x__run__mutmut_102 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_103'] = x__run__mutmut_103 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_104'] = x__run__mutmut_104 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_105'] = x__run__mutmut_105 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_106'] = x__run__mutmut_106 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_107'] = x__run__mutmut_107 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_108'] = x__run__mutmut_108 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_109'] = x__run__mutmut_109 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_110'] = x__run__mutmut_110 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_111'] = x__run__mutmut_111 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_112'] = x__run__mutmut_112 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_113'] = x__run__mutmut_113 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_114'] = x__run__mutmut_114 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_115'] = x__run__mutmut_115 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_116'] = x__run__mutmut_116 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_117'] = x__run__mutmut_117 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_118'] = x__run__mutmut_118 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_119'] = x__run__mutmut_119 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_120'] = x__run__mutmut_120 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_121'] = x__run__mutmut_121 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_122'] = x__run__mutmut_122 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_123'] = x__run__mutmut_123 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_124'] = x__run__mutmut_124 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_125'] = x__run__mutmut_125 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_126'] = x__run__mutmut_126 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_127'] = x__run__mutmut_127 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_128'] = x__run__mutmut_128 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_129'] = x__run__mutmut_129 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_130'] = x__run__mutmut_130 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_131'] = x__run__mutmut_131 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_132'] = x__run__mutmut_132 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_133'] = x__run__mutmut_133 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_134'] = x__run__mutmut_134 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_135'] = x__run__mutmut_135 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_136'] = x__run__mutmut_136 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_137'] = x__run__mutmut_137 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_138'] = x__run__mutmut_138 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_139'] = x__run__mutmut_139 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_140'] = x__run__mutmut_140 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_141'] = x__run__mutmut_141 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_142'] = x__run__mutmut_142 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_143'] = x__run__mutmut_143 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_144'] = x__run__mutmut_144 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_145'] = x__run__mutmut_145 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_146'] = x__run__mutmut_146 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_147'] = x__run__mutmut_147 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_148'] = x__run__mutmut_148 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_149'] = x__run__mutmut_149 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_150'] = x__run__mutmut_150 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_151'] = x__run__mutmut_151 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_152'] = x__run__mutmut_152 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_153'] = x__run__mutmut_153 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_154'] = x__run__mutmut_154 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_155'] = x__run__mutmut_155 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_156'] = x__run__mutmut_156 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_157'] = x__run__mutmut_157 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_158'] = x__run__mutmut_158 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_159'] = x__run__mutmut_159 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_160'] = x__run__mutmut_160 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_161'] = x__run__mutmut_161 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_162'] = x__run__mutmut_162 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_163'] = x__run__mutmut_163 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_164'] = x__run__mutmut_164 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_165'] = x__run__mutmut_165 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_166'] = x__run__mutmut_166 # type: ignore # mutmut generated
mutants_x__run__mutmut['x__run__mutmut_167'] = x__run__mutmut_167 # type: ignore # mutmut generated
mutants_x_start__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_start__mutmut)
def start(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_orig(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_1(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task or not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_2(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_3(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = None
    log.info("Alpaca WS task started")


def x_start__mutmut_4(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(None)
    log.info("Alpaca WS task started")


def x_start__mutmut_5(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(None, api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_6(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, None, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_7(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, None, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_8(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, None))
    log.info("Alpaca WS task started")


def x_start__mutmut_9(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_secret, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_10(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, tickers, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_11(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, broadcast_fn))
    log.info("Alpaca WS task started")


def x_start__mutmut_12(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, ))
    log.info("Alpaca WS task started")


def x_start__mutmut_13(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info(None)


def x_start__mutmut_14(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("XXAlpaca WS task startedXX")


def x_start__mutmut_15(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("alpaca ws task started")


def x_start__mutmut_16(api_key: str, api_secret: str, tickers: list[str], broadcast_fn: Callable) -> None:
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.create_task(_run(api_key, api_secret, tickers, broadcast_fn))
    log.info("ALPACA WS TASK STARTED")

mutants_x_start__mutmut['_mutmut_orig'] = x_start__mutmut_orig # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_1'] = x_start__mutmut_1 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_2'] = x_start__mutmut_2 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_3'] = x_start__mutmut_3 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_4'] = x_start__mutmut_4 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_5'] = x_start__mutmut_5 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_6'] = x_start__mutmut_6 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_7'] = x_start__mutmut_7 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_8'] = x_start__mutmut_8 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_9'] = x_start__mutmut_9 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_10'] = x_start__mutmut_10 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_11'] = x_start__mutmut_11 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_12'] = x_start__mutmut_12 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_13'] = x_start__mutmut_13 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_14'] = x_start__mutmut_14 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_15'] = x_start__mutmut_15 # type: ignore # mutmut generated
mutants_x_start__mutmut['x_start__mutmut_16'] = x_start__mutmut_16 # type: ignore # mutmut generated
mutants_x_stop__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_stop__mutmut)
def stop() -> None:
    global _task
    if _task and not _task.done():
        _task.cancel()


def x_stop__mutmut_orig() -> None:
    global _task
    if _task and not _task.done():
        _task.cancel()


def x_stop__mutmut_1() -> None:
    global _task
    if _task or not _task.done():
        _task.cancel()


def x_stop__mutmut_2() -> None:
    global _task
    if _task and _task.done():
        _task.cancel()

mutants_x_stop__mutmut['_mutmut_orig'] = x_stop__mutmut_orig # type: ignore # mutmut generated
mutants_x_stop__mutmut['x_stop__mutmut_1'] = x_stop__mutmut_1 # type: ignore # mutmut generated
mutants_x_stop__mutmut['x_stop__mutmut_2'] = x_stop__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_price__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_price__mutmut)
def get_price(ticker: str) -> Optional[float]:
    return _price_cache.get(ticker)


def x_get_price__mutmut_orig(ticker: str) -> Optional[float]:
    return _price_cache.get(ticker)


def x_get_price__mutmut_1(ticker: str) -> Optional[float]:
    return _price_cache.get(None)

mutants_x_get_price__mutmut['_mutmut_orig'] = x_get_price__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_price__mutmut['x_get_price__mutmut_1'] = x_get_price__mutmut_1 # type: ignore # mutmut generated
