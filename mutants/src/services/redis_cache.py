"""
Shared cache layer — Redis when REDIS_URL is set, in-memory dict otherwise.

Drop-in replacement for the scattered inline `_cache = {"data": None, "ts": 0}`
patterns across macro.py, market_data.py, sector.py, etc.

Usage:
    from services.redis_cache import cache_get, cache_set

    val = await cache_get("macro:context")
    if val is None:
        val = await expensive_fetch()
        await cache_set("macro:context", val, ttl=300)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Optional

log = logging.getLogger("signal.trade.cache")

# ── In-memory fallback (always active; used when Redis is unavailable) ─────────
_mem: dict[str, tuple[Any, float]] = {}  # key → (value, expires_at)
_mem_locks: dict[str, tuple[str, float]] = {}  # key → (token, expires_at)
_mem_lock_mutex = asyncio.Lock()  # TSYS-13c: protects the in-memory lock dict

# ── Redis client (lazily initialised) ─────────────────────────────────────────
_redis_client: Optional[Any] = None
_redis_init_tried: bool = False
_redis_init_lock = asyncio.Lock()


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__get_redis_url__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__get_redis_url__mutmut)
def _get_redis_url() -> str:
    try:
        from config import get_settings

        return get_settings().redis_url or ""
    except Exception:
        return ""


def x__get_redis_url__mutmut_orig() -> str:
    try:
        from config import get_settings

        return get_settings().redis_url or ""
    except Exception:
        return ""


def x__get_redis_url__mutmut_1() -> str:
    try:
        from config import get_settings

        return get_settings().redis_url and ""
    except Exception:
        return ""


def x__get_redis_url__mutmut_2() -> str:
    try:
        from config import get_settings

        return get_settings().redis_url or "XXXX"
    except Exception:
        return ""


def x__get_redis_url__mutmut_3() -> str:
    try:
        from config import get_settings

        return get_settings().redis_url or ""
    except Exception:
        return "XXXX"

mutants_x__get_redis_url__mutmut['_mutmut_orig'] = x__get_redis_url__mutmut_orig # type: ignore # mutmut generated
mutants_x__get_redis_url__mutmut['x__get_redis_url__mutmut_1'] = x__get_redis_url__mutmut_1 # type: ignore # mutmut generated
mutants_x__get_redis_url__mutmut['x__get_redis_url__mutmut_2'] = x__get_redis_url__mutmut_2 # type: ignore # mutmut generated
mutants_x__get_redis_url__mutmut['x__get_redis_url__mutmut_3'] = x__get_redis_url__mutmut_3 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__get_redis__mutmut)
async def _get_redis() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_orig() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_1() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = None
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_2() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = False
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_3() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = None
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_4() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_5() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = None
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_6() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(None, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_7() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=None, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_8() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=None)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_9() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_10() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_11() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, )
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_12() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=False, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_13() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=3)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_14() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = None
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_15() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(None)
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_16() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:31]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_17() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(None)
            _redis_client = None
    return _redis_client


async def x__get_redis__mutmut_18() -> Optional[Any]:
    global _redis_client, _redis_init_tried
    if _redis_init_tried:
        return _redis_client
    async with _redis_init_lock:
        if _redis_init_tried:
            return _redis_client
        _redis_init_tried = True
        url = _get_redis_url()
        if not url:
            return None
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(url, decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            _redis_client = client
            log.info(f"[cache] Redis connected: {url[:30]}…")
        except Exception as e:
            log.warning(f"[cache] Redis unavailable ({e}); using in-memory fallback")
            _redis_client = ""
    return _redis_client

mutants_x__get_redis__mutmut['_mutmut_orig'] = x__get_redis__mutmut_orig # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_1'] = x__get_redis__mutmut_1 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_2'] = x__get_redis__mutmut_2 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_3'] = x__get_redis__mutmut_3 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_4'] = x__get_redis__mutmut_4 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_5'] = x__get_redis__mutmut_5 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_6'] = x__get_redis__mutmut_6 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_7'] = x__get_redis__mutmut_7 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_8'] = x__get_redis__mutmut_8 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_9'] = x__get_redis__mutmut_9 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_10'] = x__get_redis__mutmut_10 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_11'] = x__get_redis__mutmut_11 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_12'] = x__get_redis__mutmut_12 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_13'] = x__get_redis__mutmut_13 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_14'] = x__get_redis__mutmut_14 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_15'] = x__get_redis__mutmut_15 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_16'] = x__get_redis__mutmut_16 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_17'] = x__get_redis__mutmut_17 # type: ignore # mutmut generated
mutants_x__get_redis__mutmut['x__get_redis__mutmut_18'] = x__get_redis__mutmut_18 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cache_get__mutmut)
async def cache_get(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_orig(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_1(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = None
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_2(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = None

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_3(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(None)[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_4(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split("XX:XX")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_5(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[1] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_6(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if "XX:XX" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_7(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" not in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_8(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "XXgenericXX"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_9(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "GENERIC"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_10(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = None
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_11(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_12(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = None
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_13(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(None)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_14(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_15(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(None, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_16(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, None)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_17(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_18(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, )
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_19(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(None)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_20(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(None, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_21(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, None)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_22(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_23(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, )
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_24(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(None)

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_25(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = None
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_26(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(None)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_27(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is not None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_28(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(None, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_29(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, None)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_30(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_31(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, )
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_32(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = None
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_33(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at or time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_34(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() >= expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_35(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(None, provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_36(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, None)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_37(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(provider)
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_38(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, )
        return None
    record_cache_hit(cycle_id, provider)
    return value


async def x_cache_get__mutmut_39(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(None, provider)
    return value


async def x_cache_get__mutmut_40(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, None)
    return value


async def x_cache_get__mutmut_41(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(provider)
    return value


async def x_cache_get__mutmut_42(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    from services.provider_telemetry import record_cache_hit, record_cache_miss, current_cycle_id

    cycle_id = current_cycle_id.get()
    provider = key.split(":")[0] if ":" in key else "generic"

    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                record_cache_hit(cycle_id, provider)
                return json.loads(raw)
            record_cache_miss(cycle_id, provider)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        record_cache_miss(cycle_id, provider)
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        record_cache_miss(cycle_id, provider)
        return None
    record_cache_hit(cycle_id, )
    return value

mutants_x_cache_get__mutmut['_mutmut_orig'] = x_cache_get__mutmut_orig # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_1'] = x_cache_get__mutmut_1 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_2'] = x_cache_get__mutmut_2 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_3'] = x_cache_get__mutmut_3 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_4'] = x_cache_get__mutmut_4 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_5'] = x_cache_get__mutmut_5 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_6'] = x_cache_get__mutmut_6 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_7'] = x_cache_get__mutmut_7 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_8'] = x_cache_get__mutmut_8 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_9'] = x_cache_get__mutmut_9 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_10'] = x_cache_get__mutmut_10 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_11'] = x_cache_get__mutmut_11 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_12'] = x_cache_get__mutmut_12 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_13'] = x_cache_get__mutmut_13 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_14'] = x_cache_get__mutmut_14 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_15'] = x_cache_get__mutmut_15 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_16'] = x_cache_get__mutmut_16 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_17'] = x_cache_get__mutmut_17 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_18'] = x_cache_get__mutmut_18 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_19'] = x_cache_get__mutmut_19 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_20'] = x_cache_get__mutmut_20 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_21'] = x_cache_get__mutmut_21 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_22'] = x_cache_get__mutmut_22 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_23'] = x_cache_get__mutmut_23 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_24'] = x_cache_get__mutmut_24 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_25'] = x_cache_get__mutmut_25 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_26'] = x_cache_get__mutmut_26 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_27'] = x_cache_get__mutmut_27 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_28'] = x_cache_get__mutmut_28 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_29'] = x_cache_get__mutmut_29 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_30'] = x_cache_get__mutmut_30 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_31'] = x_cache_get__mutmut_31 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_32'] = x_cache_get__mutmut_32 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_33'] = x_cache_get__mutmut_33 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_34'] = x_cache_get__mutmut_34 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_35'] = x_cache_get__mutmut_35 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_36'] = x_cache_get__mutmut_36 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_37'] = x_cache_get__mutmut_37 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_38'] = x_cache_get__mutmut_38 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_39'] = x_cache_get__mutmut_39 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_40'] = x_cache_get__mutmut_40 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_41'] = x_cache_get__mutmut_41 # type: ignore # mutmut generated
mutants_x_cache_get__mutmut['x_cache_get__mutmut_42'] = x_cache_get__mutmut_42 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cache_set__mutmut)
async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_orig(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_1(key: str, value: Any, ttl: int = 301) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_2(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = None
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_3(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_4(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(None, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_5(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, None, ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_6(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=None)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_7(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_8(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_9(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), )
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_10(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(None, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_11(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=None), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_12(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_13(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, ), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_14(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(None)

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_15(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = None
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_16(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() - ttl if ttl else 0.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_17(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 1.0
    _mem[key] = (value, expires_at)


async def x_cache_set__mutmut_18(key: str, value: Any, ttl: int = 300) -> None:
    """Store value with TTL (seconds). Serialises to JSON."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            await r.set(key, json.dumps(value, default=str), ex=ttl)
            return
    except Exception as e:
        log.debug(f"[cache] Redis set error ({key}): {e}")

    # Fallback: in-memory
    expires_at = time.monotonic() + ttl if ttl else 0.0
    _mem[key] = None

mutants_x_cache_set__mutmut['_mutmut_orig'] = x_cache_set__mutmut_orig # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_1'] = x_cache_set__mutmut_1 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_2'] = x_cache_set__mutmut_2 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_3'] = x_cache_set__mutmut_3 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_4'] = x_cache_set__mutmut_4 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_5'] = x_cache_set__mutmut_5 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_6'] = x_cache_set__mutmut_6 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_7'] = x_cache_set__mutmut_7 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_8'] = x_cache_set__mutmut_8 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_9'] = x_cache_set__mutmut_9 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_10'] = x_cache_set__mutmut_10 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_11'] = x_cache_set__mutmut_11 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_12'] = x_cache_set__mutmut_12 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_13'] = x_cache_set__mutmut_13 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_14'] = x_cache_set__mutmut_14 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_15'] = x_cache_set__mutmut_15 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_16'] = x_cache_set__mutmut_16 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_17'] = x_cache_set__mutmut_17 # type: ignore # mutmut generated
mutants_x_cache_set__mutmut['x_cache_set__mutmut_18'] = x_cache_set__mutmut_18 # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cache_delete__mutmut)
async def cache_delete(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is not None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(key, None)


async def x_cache_delete__mutmut_orig(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is not None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(key, None)


async def x_cache_delete__mutmut_1(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = None
        if r is not None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(key, None)


async def x_cache_delete__mutmut_2(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(key, None)


async def x_cache_delete__mutmut_3(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is not None:
            await r.delete(None)
            return
    except Exception:
        pass
    _mem.pop(key, None)


async def x_cache_delete__mutmut_4(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is not None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(None, None)


async def x_cache_delete__mutmut_5(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is not None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(None)


async def x_cache_delete__mutmut_6(key: str) -> None:
    """Invalidate a cache entry."""
    try:
        r = await _get_redis()
        if r is not None:
            await r.delete(key)
            return
    except Exception:
        pass
    _mem.pop(key, )

mutants_x_cache_delete__mutmut['_mutmut_orig'] = x_cache_delete__mutmut_orig # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut['x_cache_delete__mutmut_1'] = x_cache_delete__mutmut_1 # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut['x_cache_delete__mutmut_2'] = x_cache_delete__mutmut_2 # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut['x_cache_delete__mutmut_3'] = x_cache_delete__mutmut_3 # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut['x_cache_delete__mutmut_4'] = x_cache_delete__mutmut_4 # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut['x_cache_delete__mutmut_5'] = x_cache_delete__mutmut_5 # type: ignore # mutmut generated
mutants_x_cache_delete__mutmut['x_cache_delete__mutmut_6'] = x_cache_delete__mutmut_6 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cache_acquire_lock__mutmut)
async def cache_acquire_lock(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_orig(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_1(key: str, ttl: int = 301) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_2(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = None
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_3(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = None
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_4(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_5(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = None
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_6(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(None, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_7(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, None, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_8(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=None, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_9(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=None)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_10(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_11(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_12(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_13(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, )
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_14(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=False)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_15(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(None)

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_16(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = None
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_17(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = None
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_18(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(None)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_19(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing or existing[1] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_20(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[2] > now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_21(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] >= now:
            return None
        _mem_locks[key] = (token, now + ttl)
        return token


async def x_cache_acquire_lock__mutmut_22(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = None
        return token


async def x_cache_acquire_lock__mutmut_23(key: str, ttl: int = 300) -> Optional[str]:
    """Acquire a coarse distributed lock. Returns a token if acquired."""
    token = uuid.uuid4().hex
    try:
        r = await _get_redis()
        if r is not None:
            ok = await r.set(key, token, ex=ttl, nx=True)
            return token if ok else None
    except Exception as e:
        log.debug(f"[cache] Redis lock acquire error ({key}): {e}")

    # In-memory fallback — protect with asyncio.Lock to avoid TOCTOU races.
    async with _mem_lock_mutex:
        now = time.monotonic()
        existing = _mem_locks.get(key)
        if existing and existing[1] > now:
            return None
        _mem_locks[key] = (token, now - ttl)
        return token

mutants_x_cache_acquire_lock__mutmut['_mutmut_orig'] = x_cache_acquire_lock__mutmut_orig # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_1'] = x_cache_acquire_lock__mutmut_1 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_2'] = x_cache_acquire_lock__mutmut_2 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_3'] = x_cache_acquire_lock__mutmut_3 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_4'] = x_cache_acquire_lock__mutmut_4 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_5'] = x_cache_acquire_lock__mutmut_5 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_6'] = x_cache_acquire_lock__mutmut_6 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_7'] = x_cache_acquire_lock__mutmut_7 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_8'] = x_cache_acquire_lock__mutmut_8 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_9'] = x_cache_acquire_lock__mutmut_9 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_10'] = x_cache_acquire_lock__mutmut_10 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_11'] = x_cache_acquire_lock__mutmut_11 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_12'] = x_cache_acquire_lock__mutmut_12 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_13'] = x_cache_acquire_lock__mutmut_13 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_14'] = x_cache_acquire_lock__mutmut_14 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_15'] = x_cache_acquire_lock__mutmut_15 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_16'] = x_cache_acquire_lock__mutmut_16 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_17'] = x_cache_acquire_lock__mutmut_17 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_18'] = x_cache_acquire_lock__mutmut_18 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_19'] = x_cache_acquire_lock__mutmut_19 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_20'] = x_cache_acquire_lock__mutmut_20 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_21'] = x_cache_acquire_lock__mutmut_21 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_22'] = x_cache_acquire_lock__mutmut_22 # type: ignore # mutmut generated
mutants_x_cache_acquire_lock__mutmut['x_cache_acquire_lock__mutmut_23'] = x_cache_acquire_lock__mutmut_23 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cache_release_lock__mutmut)
async def cache_release_lock(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_orig(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_1(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = None
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_2(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_3(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = None
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_4(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(None, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_5(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, None, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_6(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, None, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_7(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, None)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_8(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_9(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_10(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_11(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, )
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_12(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 2, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_13(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(None)

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_14(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = None
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_15(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(None)
        if existing and existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_16(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing or existing[0] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_17(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[1] == token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_18(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] != token:
            _mem_locks.pop(key, None)


async def x_cache_release_lock__mutmut_19(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(None, None)


async def x_cache_release_lock__mutmut_20(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(None)


async def x_cache_release_lock__mutmut_21(key: str, token: str) -> None:
    """Release a lock only when the caller owns the token."""
    try:
        r = await _get_redis()
        if r is not None:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            end
            return 0
            """
            await r.eval(script, 1, key, token)
            return
    except Exception as e:
        log.debug(f"[cache] Redis lock release error ({key}): {e}")

    async with _mem_lock_mutex:
        existing = _mem_locks.get(key)
        if existing and existing[0] == token:
            _mem_locks.pop(key, )

mutants_x_cache_release_lock__mutmut['_mutmut_orig'] = x_cache_release_lock__mutmut_orig # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_1'] = x_cache_release_lock__mutmut_1 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_2'] = x_cache_release_lock__mutmut_2 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_3'] = x_cache_release_lock__mutmut_3 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_4'] = x_cache_release_lock__mutmut_4 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_5'] = x_cache_release_lock__mutmut_5 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_6'] = x_cache_release_lock__mutmut_6 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_7'] = x_cache_release_lock__mutmut_7 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_8'] = x_cache_release_lock__mutmut_8 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_9'] = x_cache_release_lock__mutmut_9 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_10'] = x_cache_release_lock__mutmut_10 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_11'] = x_cache_release_lock__mutmut_11 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_12'] = x_cache_release_lock__mutmut_12 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_13'] = x_cache_release_lock__mutmut_13 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_14'] = x_cache_release_lock__mutmut_14 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_15'] = x_cache_release_lock__mutmut_15 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_16'] = x_cache_release_lock__mutmut_16 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_17'] = x_cache_release_lock__mutmut_17 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_18'] = x_cache_release_lock__mutmut_18 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_19'] = x_cache_release_lock__mutmut_19 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_20'] = x_cache_release_lock__mutmut_20 # type: ignore # mutmut generated
mutants_x_cache_release_lock__mutmut['x_cache_release_lock__mutmut_21'] = x_cache_release_lock__mutmut_21 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cache_stats__mutmut)
def cache_stats() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_orig() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_1() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "XXbackendXX": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_2() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "BACKEND": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_3() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "XXredisXX" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_4() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "REDIS" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_5() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "XXmemoryXX",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_6() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "MEMORY",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_7() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "XXmemory_keysXX": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_8() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "MEMORY_KEYS": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_9() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "XXmemory_locksXX": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_10() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "MEMORY_LOCKS": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }


def x_cache_stats__mutmut_11() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "XXredis_connectedXX": _redis_client is not None,
    }


def x_cache_stats__mutmut_12() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "REDIS_CONNECTED": _redis_client is not None,
    }


def x_cache_stats__mutmut_13() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is None,
    }

mutants_x_cache_stats__mutmut['_mutmut_orig'] = x_cache_stats__mutmut_orig # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_1'] = x_cache_stats__mutmut_1 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_2'] = x_cache_stats__mutmut_2 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_3'] = x_cache_stats__mutmut_3 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_4'] = x_cache_stats__mutmut_4 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_5'] = x_cache_stats__mutmut_5 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_6'] = x_cache_stats__mutmut_6 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_7'] = x_cache_stats__mutmut_7 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_8'] = x_cache_stats__mutmut_8 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_9'] = x_cache_stats__mutmut_9 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_10'] = x_cache_stats__mutmut_10 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_11'] = x_cache_stats__mutmut_11 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_12'] = x_cache_stats__mutmut_12 # type: ignore # mutmut generated
mutants_x_cache_stats__mutmut['x_cache_stats__mutmut_13'] = x_cache_stats__mutmut_13 # type: ignore # mutmut generated
