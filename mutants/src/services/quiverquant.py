"""
Congressional trading signals from Quiverquant (free tier, no key needed).
Uses the bulk endpoint and filters by ticker — the per-ticker endpoint returns 404.
Bulk data is cached 4 hours; per-ticker results are cached 24 hours.
"""

import asyncio
import logging
import ssl
import time
from datetime import datetime, timedelta, timezone

log = logging.getLogger("signal.trade.congress")

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_ticker_cache: dict[str, tuple[dict, float]] = {}
_bulk_cache: dict = {"data": None, "ts": 0.0}
_bulk_lock = asyncio.Lock()

TICKER_TTL = 86400  # 24h per ticker
BULK_TTL = 14400  # 4h for the bulk fetch

_URL = "https://api.quiverquant.com/beta/live/congresstrading"
_HDRS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch_bulk__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_bulk__mutmut)
async def _fetch_bulk() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_orig() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_1() -> list:
    now = None
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_2() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None or now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_3() -> list:
    now = time.time()
    if _bulk_cache["XXdataXX"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_4() -> list:
    now = time.time()
    if _bulk_cache["DATA"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_5() -> list:
    now = time.time()
    if _bulk_cache["data"] is None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_6() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now + _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_7() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["XXtsXX"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_8() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["TS"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_9() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] <= BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_10() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["XXdataXX"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_11() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["DATA"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_12() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = None
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_13() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None or now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_14() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["XXdataXX"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_15() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["DATA"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_16() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_17() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now + _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_18() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["XXtsXX"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_19() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["TS"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_20() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] <= BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_21() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["XXdataXX"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_22() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["DATA"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_23() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = None
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_24() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=None)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_25() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=None, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_26() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=None) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_27() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_28() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, ) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_29() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(None, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_30() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=None) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_31() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_32() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, ) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_33() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=None)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_34() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=16)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_35() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status == 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_36() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 201:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_37() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] and []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_38() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["XXdataXX"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_39() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["DATA"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_40() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = None
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_41() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = None
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_42() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["XXdataXX"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_43() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["DATA"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_44() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = None
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_45() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["XXtsXX"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_46() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["TS"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_47() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(None)
        return _bulk_cache["data"] or []


async def x__fetch_bulk__mutmut_48() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["data"] and []


async def x__fetch_bulk__mutmut_49() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["XXdataXX"] or []


async def x__fetch_bulk__mutmut_50() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    async with _bulk_lock:
        now = time.time()
        if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
            return _bulk_cache["data"]
        try:
            connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
            async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
                async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        return _bulk_cache["data"] or []
                    data = await r.json(content_type=None)
            if isinstance(data, list):
                _bulk_cache["data"] = data
                _bulk_cache["ts"] = now
                return data
        except Exception as e:
            log.warning(f"[congress] bulk fetch: {e}")
        return _bulk_cache["DATA"] or []

mutants_x__fetch_bulk__mutmut['_mutmut_orig'] = x__fetch_bulk__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_1'] = x__fetch_bulk__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_2'] = x__fetch_bulk__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_3'] = x__fetch_bulk__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_4'] = x__fetch_bulk__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_5'] = x__fetch_bulk__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_6'] = x__fetch_bulk__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_7'] = x__fetch_bulk__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_8'] = x__fetch_bulk__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_9'] = x__fetch_bulk__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_10'] = x__fetch_bulk__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_11'] = x__fetch_bulk__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_12'] = x__fetch_bulk__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_13'] = x__fetch_bulk__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_14'] = x__fetch_bulk__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_15'] = x__fetch_bulk__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_16'] = x__fetch_bulk__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_17'] = x__fetch_bulk__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_18'] = x__fetch_bulk__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_19'] = x__fetch_bulk__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_20'] = x__fetch_bulk__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_21'] = x__fetch_bulk__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_22'] = x__fetch_bulk__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_23'] = x__fetch_bulk__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_24'] = x__fetch_bulk__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_25'] = x__fetch_bulk__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_26'] = x__fetch_bulk__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_27'] = x__fetch_bulk__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_28'] = x__fetch_bulk__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_29'] = x__fetch_bulk__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_30'] = x__fetch_bulk__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_31'] = x__fetch_bulk__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_32'] = x__fetch_bulk__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_33'] = x__fetch_bulk__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_34'] = x__fetch_bulk__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_35'] = x__fetch_bulk__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_36'] = x__fetch_bulk__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_37'] = x__fetch_bulk__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_38'] = x__fetch_bulk__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_39'] = x__fetch_bulk__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_40'] = x__fetch_bulk__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_41'] = x__fetch_bulk__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_42'] = x__fetch_bulk__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_43'] = x__fetch_bulk__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_44'] = x__fetch_bulk__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_45'] = x__fetch_bulk__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_46'] = x__fetch_bulk__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_47'] = x__fetch_bulk__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_48'] = x__fetch_bulk__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_49'] = x__fetch_bulk__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_bulk__mutmut['x__fetch_bulk__mutmut_50'] = x__fetch_bulk__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_congress_signal__mutmut)
async def get_congress_signal(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_orig(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_1(ticker: str) -> dict:
    cached = None
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_2(ticker: str) -> dict:
    cached = _ticker_cache.get(None)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_3(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached or time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_4(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() + cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_5(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[2] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_6(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] <= TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_7(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[1]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_8(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = None
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_9(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_10(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = None
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_11(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_12(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(None).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_13(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=None)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_14(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=91)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_15(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = None

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_16(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").lower() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_17(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get(None, "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_18(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", None).upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_19(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_20(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", ).upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_21(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("XXTickerXX", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_22(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_23(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("TICKER", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_24(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "XXXX").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_25(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() == ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_26(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.lower():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_27(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                break
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_28(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = None
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_29(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") and ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_30(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") and t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_31(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get(None) or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_32(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("XXTransactionDateXX") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_33(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("transactiondate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_34(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TRANSACTIONDATE") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_35(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get(None) or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_36(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("XXReportDateXX") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_37(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("reportdate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_38(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("REPORTDATE") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_39(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or "XXXX"
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_40(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = None
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_41(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(None, "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_42(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], None)
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_43(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime("%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_44(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], )
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_45(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:11], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_46(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "XX%Y-%m-%dXX")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_47(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_48(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%M-%D")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_49(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                break
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_50(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date <= cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_51(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                break
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_52(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = None
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_53(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").upper()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_54(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get(None, "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_55(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", None).lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_56(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_57(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", ).lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_58(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("XXTransactionXX", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_59(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_60(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("TRANSACTION", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_61(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "XXXX").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_62(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = None
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_63(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get(None, "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_64(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", None)
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_65(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_66(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", )
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_67(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("XXRepresentativeXX", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_68(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_69(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("REPRESENTATIVE", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_70(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "XX?XX")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_71(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = None
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_72(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get(None, t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_73(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", None)
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_74(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get(t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_75(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", )
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_76(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("XXRangeXX", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_77(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_78(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("RANGE", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_79(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get(None, ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_80(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", None))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_81(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get(""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_82(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_83(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("XXAmountXX", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_84(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_85(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("AMOUNT", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_86(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", "XXXX"))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_87(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = None
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_88(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"XXrepXX": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_89(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"REP": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_90(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "XXamountXX": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_91(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "AMOUNT": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_92(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "XXdateXX": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_93(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "DATE": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_94(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime(None)}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_95(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("XX%Y-%m-%dXX")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_96(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_97(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%M-%D")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_98(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn and "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_99(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "XXpurchaseXX" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_100(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "PURCHASE" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_101(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" not in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_102(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "XXbuyXX" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_103(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "BUY" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_104(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" not in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_105(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(None)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_106(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn and "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_107(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "XXsaleXX" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_108(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "SALE" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_109(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" not in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_110(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "XXsellXX" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_111(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "SELL" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_112(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" not in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_113(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(None)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_114(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = None
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_115(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = None

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_116(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb + ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_117(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net > 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_118(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 4:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_119(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = None
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_120(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "XXbullishXX", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_121(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "BULLISH", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_122(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 9
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_123(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net > 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_124(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 2:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_125(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = None
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_126(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "XXbullishXX", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_127(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "BULLISH", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_128(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 5
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_129(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net < -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_130(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= +3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_131(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -4:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_132(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = None
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_133(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "XXbearishXX", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_134(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "BEARISH", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_135(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", +8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_136(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -9
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_137(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net < -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_138(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= +1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_139(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -2:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_140(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = None
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_141(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "XXbearishXX", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_142(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "BEARISH", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_143(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", +4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_144(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -5
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_145(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = None

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_146(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "XXneutralXX", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_147(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "NEUTRAL", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_148(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 1

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_149(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = None
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_150(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "XXbuysXX": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_151(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "BUYS": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_152(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "XXsellsXX": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_153(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "SELLS": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_154(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "XXnetXX": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_155(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "NET": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_156(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "XXsignalXX": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_157(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "SIGNAL": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_158(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "XXscoreXX": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_159(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "SCORE": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_160(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "XXrecent_buysXX": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_161(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "RECENT_BUYS": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_162(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:4],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_163(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "XXrecent_sellsXX": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_164(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "RECENT_SELLS": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_165(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:4],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_166(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = None
        return result

    except Exception as e:
        log.warning(f"[congress] {ticker}: {e}")
        return {}


async def x_get_congress_signal__mutmut_167(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish", 8
        elif net >= 1:
            signal, score = "bullish", 4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "buys": nb,
            "sells": ns,
            "net": net,
            "signal": signal,
            "score": score,
            "recent_buys": recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        log.warning(None)
        return {}

mutants_x_get_congress_signal__mutmut['_mutmut_orig'] = x_get_congress_signal__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_1'] = x_get_congress_signal__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_2'] = x_get_congress_signal__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_3'] = x_get_congress_signal__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_4'] = x_get_congress_signal__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_5'] = x_get_congress_signal__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_6'] = x_get_congress_signal__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_7'] = x_get_congress_signal__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_8'] = x_get_congress_signal__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_9'] = x_get_congress_signal__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_10'] = x_get_congress_signal__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_11'] = x_get_congress_signal__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_12'] = x_get_congress_signal__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_13'] = x_get_congress_signal__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_14'] = x_get_congress_signal__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_15'] = x_get_congress_signal__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_16'] = x_get_congress_signal__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_17'] = x_get_congress_signal__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_18'] = x_get_congress_signal__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_19'] = x_get_congress_signal__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_20'] = x_get_congress_signal__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_21'] = x_get_congress_signal__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_22'] = x_get_congress_signal__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_23'] = x_get_congress_signal__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_24'] = x_get_congress_signal__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_25'] = x_get_congress_signal__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_26'] = x_get_congress_signal__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_27'] = x_get_congress_signal__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_28'] = x_get_congress_signal__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_29'] = x_get_congress_signal__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_30'] = x_get_congress_signal__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_31'] = x_get_congress_signal__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_32'] = x_get_congress_signal__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_33'] = x_get_congress_signal__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_34'] = x_get_congress_signal__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_35'] = x_get_congress_signal__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_36'] = x_get_congress_signal__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_37'] = x_get_congress_signal__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_38'] = x_get_congress_signal__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_39'] = x_get_congress_signal__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_40'] = x_get_congress_signal__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_41'] = x_get_congress_signal__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_42'] = x_get_congress_signal__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_43'] = x_get_congress_signal__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_44'] = x_get_congress_signal__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_45'] = x_get_congress_signal__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_46'] = x_get_congress_signal__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_47'] = x_get_congress_signal__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_48'] = x_get_congress_signal__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_49'] = x_get_congress_signal__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_50'] = x_get_congress_signal__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_51'] = x_get_congress_signal__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_52'] = x_get_congress_signal__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_53'] = x_get_congress_signal__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_54'] = x_get_congress_signal__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_55'] = x_get_congress_signal__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_56'] = x_get_congress_signal__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_57'] = x_get_congress_signal__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_58'] = x_get_congress_signal__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_59'] = x_get_congress_signal__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_60'] = x_get_congress_signal__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_61'] = x_get_congress_signal__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_62'] = x_get_congress_signal__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_63'] = x_get_congress_signal__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_64'] = x_get_congress_signal__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_65'] = x_get_congress_signal__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_66'] = x_get_congress_signal__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_67'] = x_get_congress_signal__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_68'] = x_get_congress_signal__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_69'] = x_get_congress_signal__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_70'] = x_get_congress_signal__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_71'] = x_get_congress_signal__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_72'] = x_get_congress_signal__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_73'] = x_get_congress_signal__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_74'] = x_get_congress_signal__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_75'] = x_get_congress_signal__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_76'] = x_get_congress_signal__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_77'] = x_get_congress_signal__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_78'] = x_get_congress_signal__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_79'] = x_get_congress_signal__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_80'] = x_get_congress_signal__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_81'] = x_get_congress_signal__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_82'] = x_get_congress_signal__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_83'] = x_get_congress_signal__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_84'] = x_get_congress_signal__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_85'] = x_get_congress_signal__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_86'] = x_get_congress_signal__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_87'] = x_get_congress_signal__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_88'] = x_get_congress_signal__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_89'] = x_get_congress_signal__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_90'] = x_get_congress_signal__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_91'] = x_get_congress_signal__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_92'] = x_get_congress_signal__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_93'] = x_get_congress_signal__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_94'] = x_get_congress_signal__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_95'] = x_get_congress_signal__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_96'] = x_get_congress_signal__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_97'] = x_get_congress_signal__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_98'] = x_get_congress_signal__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_99'] = x_get_congress_signal__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_100'] = x_get_congress_signal__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_101'] = x_get_congress_signal__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_102'] = x_get_congress_signal__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_103'] = x_get_congress_signal__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_104'] = x_get_congress_signal__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_105'] = x_get_congress_signal__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_106'] = x_get_congress_signal__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_107'] = x_get_congress_signal__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_108'] = x_get_congress_signal__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_109'] = x_get_congress_signal__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_110'] = x_get_congress_signal__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_111'] = x_get_congress_signal__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_112'] = x_get_congress_signal__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_113'] = x_get_congress_signal__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_114'] = x_get_congress_signal__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_115'] = x_get_congress_signal__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_116'] = x_get_congress_signal__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_117'] = x_get_congress_signal__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_118'] = x_get_congress_signal__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_119'] = x_get_congress_signal__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_120'] = x_get_congress_signal__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_121'] = x_get_congress_signal__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_122'] = x_get_congress_signal__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_123'] = x_get_congress_signal__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_124'] = x_get_congress_signal__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_125'] = x_get_congress_signal__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_126'] = x_get_congress_signal__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_127'] = x_get_congress_signal__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_128'] = x_get_congress_signal__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_129'] = x_get_congress_signal__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_130'] = x_get_congress_signal__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_131'] = x_get_congress_signal__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_132'] = x_get_congress_signal__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_133'] = x_get_congress_signal__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_134'] = x_get_congress_signal__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_135'] = x_get_congress_signal__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_136'] = x_get_congress_signal__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_137'] = x_get_congress_signal__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_138'] = x_get_congress_signal__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_139'] = x_get_congress_signal__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_140'] = x_get_congress_signal__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_141'] = x_get_congress_signal__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_142'] = x_get_congress_signal__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_143'] = x_get_congress_signal__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_144'] = x_get_congress_signal__mutmut_144 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_145'] = x_get_congress_signal__mutmut_145 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_146'] = x_get_congress_signal__mutmut_146 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_147'] = x_get_congress_signal__mutmut_147 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_148'] = x_get_congress_signal__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_149'] = x_get_congress_signal__mutmut_149 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_150'] = x_get_congress_signal__mutmut_150 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_151'] = x_get_congress_signal__mutmut_151 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_152'] = x_get_congress_signal__mutmut_152 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_153'] = x_get_congress_signal__mutmut_153 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_154'] = x_get_congress_signal__mutmut_154 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_155'] = x_get_congress_signal__mutmut_155 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_156'] = x_get_congress_signal__mutmut_156 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_157'] = x_get_congress_signal__mutmut_157 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_158'] = x_get_congress_signal__mutmut_158 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_159'] = x_get_congress_signal__mutmut_159 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_160'] = x_get_congress_signal__mutmut_160 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_161'] = x_get_congress_signal__mutmut_161 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_162'] = x_get_congress_signal__mutmut_162 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_163'] = x_get_congress_signal__mutmut_163 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_164'] = x_get_congress_signal__mutmut_164 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_165'] = x_get_congress_signal__mutmut_165 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_166'] = x_get_congress_signal__mutmut_166 # type: ignore # mutmut generated
mutants_x_get_congress_signal__mutmut['x_get_congress_signal__mutmut_167'] = x_get_congress_signal__mutmut_167 # type: ignore # mutmut generated
