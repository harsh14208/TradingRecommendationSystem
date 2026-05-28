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

import json
import logging
import time
import uuid
from typing import Any, Optional

log = logging.getLogger("signal.trade.cache")

# ── In-memory fallback (always active; used when Redis is unavailable) ─────────
_mem: dict[str, tuple[Any, float]] = {}  # key → (value, expires_at)
_mem_locks: dict[str, tuple[str, float]] = {}  # key → (token, expires_at)


# ── Redis client (lazily initialised) ─────────────────────────────────────────
_redis_client: Optional[Any] = None
_redis_init_tried: bool = False


def _get_redis_url() -> str:
    try:
        from config import get_settings

        return get_settings().redis_url or ""
    except Exception:
        return ""


async def _get_redis() -> Optional[Any]:
    global _redis_client, _redis_init_tried
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


async def cache_get(key: str) -> Optional[Any]:
    """Return cached value or None if missing / expired."""
    # Try Redis first
    try:
        r = await _get_redis()
        if r is not None:
            raw = await r.get(key)
            if raw is not None:
                return json.loads(raw)
            return None
    except Exception as e:
        log.debug(f"[cache] Redis get error ({key}): {e}")

    # Fallback: in-memory
    entry = _mem.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if expires_at and time.monotonic() > expires_at:
        del _mem[key]
        return None
    return value


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

    now = time.monotonic()
    existing = _mem_locks.get(key)
    if existing and existing[1] > now:
        return None
    _mem_locks[key] = (token, now + ttl)
    return token


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

    existing = _mem_locks.get(key)
    if existing and existing[0] == token:
        _mem_locks.pop(key, None)


def cache_stats() -> dict:
    """Return basic cache stats for the /api/admin/rate-limits endpoint."""
    return {
        "backend": "redis" if _redis_client else "memory",
        "memory_keys": len(_mem),
        "memory_locks": len(_mem_locks),
        "redis_connected": _redis_client is not None,
    }
