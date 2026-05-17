import pytest

from services import redis_cache


@pytest.mark.asyncio
async def test_memory_lock_acquire_release_roundtrip():
    redis_cache._mem_locks.clear()
    token = await redis_cache.cache_acquire_lock("test-lock", ttl=30)
    assert token

    second = await redis_cache.cache_acquire_lock("test-lock", ttl=30)
    assert second is None

    await redis_cache.cache_release_lock("test-lock", token)
    third = await redis_cache.cache_acquire_lock("test-lock", ttl=30)
    assert third
    await redis_cache.cache_release_lock("test-lock", third)
