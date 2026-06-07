"""Unit tests for services/market_data.py — pure helpers and cache."""
import time
import threading
from unittest.mock import patch

import pandas as pd
import pytest


# ── _yf_is_blocked / _yf_trip_breaker ────────────────────────────────────────

def test_yf_is_blocked_initially_false():
    import services.market_data as md
    # Reset backoff
    md._yf_backoff_until = 0
    from services.market_data import _yf_is_blocked
    assert _yf_is_blocked() is False


def test_yf_trip_breaker_blocks():
    import services.market_data as md
    from services.market_data import _yf_trip_breaker, _yf_is_blocked
    md._yf_backoff_until = 0
    _yf_trip_breaker()
    assert _yf_is_blocked() is True
    # Reset
    md._yf_backoff_until = 0


# ── _get_fetch_lock ───────────────────────────────────────────────────────────

def test_get_fetch_lock_returns_lock():
    from services.market_data import _get_fetch_lock
    lock = _get_fetch_lock(("AAPL", "3mo", "1d"))
    assert isinstance(lock, type(threading.Lock()))


def test_get_fetch_lock_same_key_returns_same():
    from services.market_data import _get_fetch_lock
    k = ("AAPL", "3mo", "1d")
    lock1 = _get_fetch_lock(k)
    lock2 = _get_fetch_lock(k)
    assert lock1 is lock2


def test_get_fetch_lock_different_keys_different():
    from services.market_data import _get_fetch_lock
    lock1 = _get_fetch_lock(("AAPL", "1mo", "1d"))
    lock2 = _get_fetch_lock(("NVDA", "1mo", "1d"))
    assert lock1 is not lock2


def test_get_fetch_lock_eviction_at_cap():
    import services.market_data as md
    from services.market_data import _get_fetch_lock
    original_locks = dict(md._fetch_locks)
    # Fill to cap
    md._fetch_locks.clear()
    for i in range(md._FETCH_LOCKS_MAX):
        md._fetch_locks[(f"TICKER{i}", "3mo", "1d")] = threading.Lock()
    # Requesting a new key should evict half
    _get_fetch_lock(("NEW_TICKER_OVERFLOW", "3mo", "1d"))
    assert len(md._fetch_locks) <= md._FETCH_LOCKS_MAX
    # Restore
    md._fetch_locks.clear()
    md._fetch_locks.update(original_locks)


# ── _ohlcv_cache_get / _ohlcv_cache_set ─────────────────────────────────────

def test_ohlcv_cache_miss():
    import services.market_data as md
    md._redis_client = None
    md._ohlcv_cache = {}
    from services.market_data import _ohlcv_cache_get
    assert _ohlcv_cache_get(("AAPL", "3mo", "1d")) is None


def test_ohlcv_cache_set_and_get():
    import services.market_data as md
    md._redis_client = None
    md._ohlcv_cache = {}
    from services.market_data import _ohlcv_cache_get, _ohlcv_cache_set

    df = pd.DataFrame({"Close": [100.0, 101.0]})
    key = ("AAPL", "3mo", "1d")
    _ohlcv_cache_set(key, df, time.time())
    result = _ohlcv_cache_get(key)
    assert result is not None
    assert len(result) == 2

    # Cleanup
    del md._ohlcv_cache[key]


def test_ohlcv_cache_expired():
    import services.market_data as md
    md._redis_client = None
    from services.market_data import _ohlcv_cache_get

    key = ("NVDA", "3mo", "1d")
    md._ohlcv_cache[key] = {"df": pd.DataFrame({"Close": [500.0]}), "ts": 0.0}
    result = _ohlcv_cache_get(key)
    assert result is None  # expired
    del md._ohlcv_cache[key]


def test_ohlcv_cache_set_evicts_at_max():
    import services.market_data as md
    md._redis_client = None
    from services.market_data import _ohlcv_cache_set
    original = dict(md._ohlcv_cache)
    md._ohlcv_cache.clear()
    # Fill to max
    for i in range(md._OHLCV_MAX_ENTRIES):
        md._ohlcv_cache[(f"T{i}", "3mo", "1d")] = {"df": pd.DataFrame(), "ts": time.time()}
    # Adding one more should trigger eviction
    _ohlcv_cache_set(("AAPL_NEW", "3mo", "1d"), pd.DataFrame(), time.time())
    assert len(md._ohlcv_cache) <= md._OHLCV_MAX_ENTRIES
    # Restore
    md._ohlcv_cache.clear()
    md._ohlcv_cache.update(original)


# ── _retry ────────────────────────────────────────────────────────────────────

def test_retry_success():
    import services.market_data as md
    from services.market_data import _retry
    md._yf_backoff_until = 0

    results = []
    def fn():
        results.append(1)
        return "ok"

    result = _retry(fn, retries=2, base_delay=0.0)
    assert result == "ok"
    assert len(results) == 1


def test_retry_blocked():
    import services.market_data as md
    from services.market_data import _retry
    md._yf_backoff_until = time.time() + 9999  # blocked

    with pytest.raises(RuntimeError, match="circuit breaker"):
        _retry(lambda: "ok")

    md._yf_backoff_until = 0


def test_retry_eventual_success():
    import services.market_data as md
    from services.market_data import _retry
    md._yf_backoff_until = 0

    calls = [0]
    def fn():
        calls[0] += 1
        if calls[0] < 3:
            raise ValueError("transient error")
        return "success"

    result = _retry(fn, retries=4, base_delay=0.0)
    assert result == "success"


def test_retry_429_trips_breaker():
    import services.market_data as md
    from services.market_data import _retry
    md._yf_backoff_until = 0

    def fn():
        raise Exception("429 Too Many Requests rate limit exceeded")

    with pytest.raises(RuntimeError, match="429"):
        _retry(fn, retries=2, base_delay=0.0)

    assert md._yf_is_blocked() is True
    md._yf_backoff_until = 0


def test_retry_exhausts_retries():
    import services.market_data as md
    from services.market_data import _retry
    md._yf_backoff_until = 0

    def fn():
        raise ValueError("persistent error")

    with pytest.raises(ValueError):
        _retry(fn, retries=2, base_delay=0.0)


# ── get_quote ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_quote_returns_dict():
    from services.market_data import get_quote
    with patch("services.market_data._rate_limited", return_value={"price": 150.0, "ticker": "AAPL"}):
        result = await get_quote("AAPL")
    assert isinstance(result, dict)


# ── get_quotes ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_quotes_empty():
    from services.market_data import get_quotes
    with patch("services.market_data._rate_limited", return_value=[]):
        result = await get_quotes([])
    assert result == []
