"""
Market Calendar — upcoming NYSE holidays from Polygon v1/marketstatus/upcoming.

Used by scanner._maybe_send() to apply a -5pp confidence haircut on all signals
when a 3-day weekend is 2 trading days away (lower liquidity, wider spreads, gap risk).

Cache: 24 hours (holiday schedule doesn't change intraday).
"""

import logging
import os
import time
from datetime import datetime, timezone

import aiohttp
from services.http_client import get_ssl_context, shared_session

log = logging.getLogger("signal.trade.market_calendar")

_cache: dict = {"data": None, "ts": 0.0}
_TTL = 86400  # 24 hours


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_upcoming_holidays__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_upcoming_holidays__mutmut)
async def get_upcoming_holidays() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_orig() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_1() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = None
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_2() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None or now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_3() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["XXdataXX"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_4() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["DATA"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_5() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_6() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now + _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_7() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["XXtsXX"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_8() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["TS"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_9() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] <= _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_10() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["XXdataXX"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_11() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["DATA"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_12() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = None
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_13() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") and ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_14() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") and os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_15() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv(None) or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_16() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("XXPOLYGON_API_KEYXX") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_17() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("polygon_api_key") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_18() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv(None) or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_19() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("XXMASSIVE_API_KEYXX") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_20() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("massive_api_key") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_21() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or "XXXX"
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_22() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_23() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = None
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_24() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["XXdataXX"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_25() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["DATA"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_26() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = None
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_27() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["XXtsXX"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_28() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["TS"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_29() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = None
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_30() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                None,
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_31() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params=None,
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_32() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=None,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_33() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=None,
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_34() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_35() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_36() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_37() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_38() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "XXhttps://api.polygon.io/v1/marketstatus/upcomingXX",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_39() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "HTTPS://API.POLYGON.IO/V1/MARKETSTATUS/UPCOMING",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_40() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"XXapiKeyXX": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_41() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apikey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_42() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"APIKEY": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_43() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=None),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_44() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=7),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_45() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status == 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_46() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 201:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_47() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = None
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_48() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["XXdataXX"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_49() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["DATA"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_50() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = None
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_51() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["XXtsXX"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_52() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["TS"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_53() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = None
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_54() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(None)
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_55() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = None
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_56() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["XXdataXX"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_57() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["DATA"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_58() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = None
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_59() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["XXtsXX"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_60() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["TS"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_61() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = None
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_62() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" or item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_63() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get(None) == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_64() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("XXstatusXX") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_65() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("STATUS") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_66() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") != "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_67() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "XXclosedXX" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_68() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "CLOSED" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_69() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get(None) in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_70() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("XXexchangeXX") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_71() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("EXCHANGE") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_72() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") not in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_73() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("XXNYSEXX", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_74() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("nyse", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_75() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "XXNASDAQXX"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_76() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "nasdaq"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_77() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                None
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_78() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "XXdateXX": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_79() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "DATE": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_80() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get(None, ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_81() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", None),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_82() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get(""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_83() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_84() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("XXdateXX", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_85() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("DATE", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_86() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", "XXXX"),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_87() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "XXnameXX": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_88() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "NAME": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_89() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get(None, "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_90() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", None),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_91() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_92() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", ),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_93() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("XXnameXX", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_94() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("NAME", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_95() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "XXHolidayXX"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_96() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_97() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "HOLIDAY"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_98() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "XXexchangeXX": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_99() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "EXCHANGE": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_100() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get(None, "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_101() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", None),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_102() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_103() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", ),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_104() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("XXexchangeXX", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_105() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("EXCHANGE", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_106() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "XXNYSEXX"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_107() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "nyse"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_108() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = None
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_109() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["XXdataXX"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_110() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["DATA"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_111() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = None
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_112() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["XXtsXX"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_113() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["TS"] = now
    if holidays:
        log.debug(f"[market_calendar] {len(holidays)} upcoming holidays loaded")
    return holidays


async def x_get_upcoming_holidays__mutmut_114() -> list[dict]:
    """
    Returns list of upcoming market holidays from Polygon.
    Each entry: {"date": "2026-05-26", "name": "Memorial Day", "exchange": "NYSE"}
    Falls back to empty list if Polygon unavailable.
    """
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
    if not api_key:
        _cache["data"] = []
        _cache["ts"] = now
        return []

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(
                "https://api.polygon.io/v1/marketstatus/upcoming",
                params={"apiKey": api_key},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=6),
            ) as resp:
                if resp.status != 200:
                    _cache["data"] = []
                    _cache["ts"] = now
                    return []
                data = await resp.json()
    except Exception as e:
        log.debug(f"[market_calendar] fetch failed: {e}")
        _cache["data"] = []
        _cache["ts"] = now
        return []

    holidays = []
    for item in data if isinstance(data, list) else []:
        if item.get("status") == "closed" and item.get("exchange") in ("NYSE", "NASDAQ"):
            holidays.append(
                {
                    "date": item.get("date", ""),
                    "name": item.get("name", "Holiday"),
                    "exchange": item.get("exchange", "NYSE"),
                }
            )

    _cache["data"] = holidays
    _cache["ts"] = now
    if holidays:
        log.debug(None)
    return holidays

mutants_x_get_upcoming_holidays__mutmut['_mutmut_orig'] = x_get_upcoming_holidays__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_1'] = x_get_upcoming_holidays__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_2'] = x_get_upcoming_holidays__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_3'] = x_get_upcoming_holidays__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_4'] = x_get_upcoming_holidays__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_5'] = x_get_upcoming_holidays__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_6'] = x_get_upcoming_holidays__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_7'] = x_get_upcoming_holidays__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_8'] = x_get_upcoming_holidays__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_9'] = x_get_upcoming_holidays__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_10'] = x_get_upcoming_holidays__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_11'] = x_get_upcoming_holidays__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_12'] = x_get_upcoming_holidays__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_13'] = x_get_upcoming_holidays__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_14'] = x_get_upcoming_holidays__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_15'] = x_get_upcoming_holidays__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_16'] = x_get_upcoming_holidays__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_17'] = x_get_upcoming_holidays__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_18'] = x_get_upcoming_holidays__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_19'] = x_get_upcoming_holidays__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_20'] = x_get_upcoming_holidays__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_21'] = x_get_upcoming_holidays__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_22'] = x_get_upcoming_holidays__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_23'] = x_get_upcoming_holidays__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_24'] = x_get_upcoming_holidays__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_25'] = x_get_upcoming_holidays__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_26'] = x_get_upcoming_holidays__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_27'] = x_get_upcoming_holidays__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_28'] = x_get_upcoming_holidays__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_29'] = x_get_upcoming_holidays__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_30'] = x_get_upcoming_holidays__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_31'] = x_get_upcoming_holidays__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_32'] = x_get_upcoming_holidays__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_33'] = x_get_upcoming_holidays__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_34'] = x_get_upcoming_holidays__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_35'] = x_get_upcoming_holidays__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_36'] = x_get_upcoming_holidays__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_37'] = x_get_upcoming_holidays__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_38'] = x_get_upcoming_holidays__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_39'] = x_get_upcoming_holidays__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_40'] = x_get_upcoming_holidays__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_41'] = x_get_upcoming_holidays__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_42'] = x_get_upcoming_holidays__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_43'] = x_get_upcoming_holidays__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_44'] = x_get_upcoming_holidays__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_45'] = x_get_upcoming_holidays__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_46'] = x_get_upcoming_holidays__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_47'] = x_get_upcoming_holidays__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_48'] = x_get_upcoming_holidays__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_49'] = x_get_upcoming_holidays__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_50'] = x_get_upcoming_holidays__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_51'] = x_get_upcoming_holidays__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_52'] = x_get_upcoming_holidays__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_53'] = x_get_upcoming_holidays__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_54'] = x_get_upcoming_holidays__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_55'] = x_get_upcoming_holidays__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_56'] = x_get_upcoming_holidays__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_57'] = x_get_upcoming_holidays__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_58'] = x_get_upcoming_holidays__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_59'] = x_get_upcoming_holidays__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_60'] = x_get_upcoming_holidays__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_61'] = x_get_upcoming_holidays__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_62'] = x_get_upcoming_holidays__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_63'] = x_get_upcoming_holidays__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_64'] = x_get_upcoming_holidays__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_65'] = x_get_upcoming_holidays__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_66'] = x_get_upcoming_holidays__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_67'] = x_get_upcoming_holidays__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_68'] = x_get_upcoming_holidays__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_69'] = x_get_upcoming_holidays__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_70'] = x_get_upcoming_holidays__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_71'] = x_get_upcoming_holidays__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_72'] = x_get_upcoming_holidays__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_73'] = x_get_upcoming_holidays__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_74'] = x_get_upcoming_holidays__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_75'] = x_get_upcoming_holidays__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_76'] = x_get_upcoming_holidays__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_77'] = x_get_upcoming_holidays__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_78'] = x_get_upcoming_holidays__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_79'] = x_get_upcoming_holidays__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_80'] = x_get_upcoming_holidays__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_81'] = x_get_upcoming_holidays__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_82'] = x_get_upcoming_holidays__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_83'] = x_get_upcoming_holidays__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_84'] = x_get_upcoming_holidays__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_85'] = x_get_upcoming_holidays__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_86'] = x_get_upcoming_holidays__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_87'] = x_get_upcoming_holidays__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_88'] = x_get_upcoming_holidays__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_89'] = x_get_upcoming_holidays__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_90'] = x_get_upcoming_holidays__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_91'] = x_get_upcoming_holidays__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_92'] = x_get_upcoming_holidays__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_93'] = x_get_upcoming_holidays__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_94'] = x_get_upcoming_holidays__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_95'] = x_get_upcoming_holidays__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_96'] = x_get_upcoming_holidays__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_97'] = x_get_upcoming_holidays__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_98'] = x_get_upcoming_holidays__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_99'] = x_get_upcoming_holidays__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_100'] = x_get_upcoming_holidays__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_101'] = x_get_upcoming_holidays__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_102'] = x_get_upcoming_holidays__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_103'] = x_get_upcoming_holidays__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_104'] = x_get_upcoming_holidays__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_105'] = x_get_upcoming_holidays__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_106'] = x_get_upcoming_holidays__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_107'] = x_get_upcoming_holidays__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_108'] = x_get_upcoming_holidays__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_109'] = x_get_upcoming_holidays__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_110'] = x_get_upcoming_holidays__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_111'] = x_get_upcoming_holidays__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_112'] = x_get_upcoming_holidays__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_113'] = x_get_upcoming_holidays__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_upcoming_holidays__mutmut['x_get_upcoming_holidays__mutmut_114'] = x_get_upcoming_holidays__mutmut_114 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_is_pre_long_weekend__mutmut)
def is_pre_long_weekend(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_orig(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_1(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = None
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_2(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(None).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_3(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = None
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_4(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(None, "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_5(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], None).date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_6(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime("%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_7(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], ).date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_8(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["XXdateXX"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_9(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["DATE"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_10(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "XX%Y-%m-%dXX").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_11(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_12(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%M-%D").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_13(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            break
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_14(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = None
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_15(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate + today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_16(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 and days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_17(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until <= 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_18(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 1 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_19(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until >= 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_20(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 6:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_21(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            break
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_22(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = None  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_23(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday not in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_24(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (1, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_25(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 5):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_26(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until < 3:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_27(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 4:
                return True, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_28(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return False, h["name"]
    return False, ""


def x_is_pre_long_weekend__mutmut_29(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["XXnameXX"]
    return False, ""


def x_is_pre_long_weekend__mutmut_30(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["NAME"]
    return False, ""


def x_is_pre_long_weekend__mutmut_31(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return True, ""


def x_is_pre_long_weekend__mutmut_32(holidays: list[dict]) -> tuple[bool, str]:
    """
    Returns (True, holiday_name) if today is within 2 trading days of a 3-day weekend.
    A 3-day weekend means the holiday lands on a Friday or Monday so the market
    is closed for 3 consecutive calendar days.
    Returns (False, "") otherwise.
    """
    today = datetime.now(timezone.utc).date()
    for h in holidays:
        try:
            hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        # Only care about near-term holidays (next 5 calendar days)
        days_until = (hdate - today).days
        if days_until < 0 or days_until > 5:
            continue
        # Check if it creates a 3-day weekend (Mon or Fri holiday)
        weekday = hdate.weekday()  # 0=Mon … 4=Fri
        if weekday in (0, 4):  # Monday or Friday holiday → 3-day weekend
            # Are we within 2 trading days?
            # Approximate: 2 trading days ≈ 2-3 calendar days before
            if days_until <= 3:
                return True, h["name"]
    return False, "XXXX"

mutants_x_is_pre_long_weekend__mutmut['_mutmut_orig'] = x_is_pre_long_weekend__mutmut_orig # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_1'] = x_is_pre_long_weekend__mutmut_1 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_2'] = x_is_pre_long_weekend__mutmut_2 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_3'] = x_is_pre_long_weekend__mutmut_3 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_4'] = x_is_pre_long_weekend__mutmut_4 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_5'] = x_is_pre_long_weekend__mutmut_5 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_6'] = x_is_pre_long_weekend__mutmut_6 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_7'] = x_is_pre_long_weekend__mutmut_7 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_8'] = x_is_pre_long_weekend__mutmut_8 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_9'] = x_is_pre_long_weekend__mutmut_9 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_10'] = x_is_pre_long_weekend__mutmut_10 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_11'] = x_is_pre_long_weekend__mutmut_11 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_12'] = x_is_pre_long_weekend__mutmut_12 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_13'] = x_is_pre_long_weekend__mutmut_13 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_14'] = x_is_pre_long_weekend__mutmut_14 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_15'] = x_is_pre_long_weekend__mutmut_15 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_16'] = x_is_pre_long_weekend__mutmut_16 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_17'] = x_is_pre_long_weekend__mutmut_17 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_18'] = x_is_pre_long_weekend__mutmut_18 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_19'] = x_is_pre_long_weekend__mutmut_19 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_20'] = x_is_pre_long_weekend__mutmut_20 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_21'] = x_is_pre_long_weekend__mutmut_21 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_22'] = x_is_pre_long_weekend__mutmut_22 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_23'] = x_is_pre_long_weekend__mutmut_23 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_24'] = x_is_pre_long_weekend__mutmut_24 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_25'] = x_is_pre_long_weekend__mutmut_25 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_26'] = x_is_pre_long_weekend__mutmut_26 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_27'] = x_is_pre_long_weekend__mutmut_27 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_28'] = x_is_pre_long_weekend__mutmut_28 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_29'] = x_is_pre_long_weekend__mutmut_29 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_30'] = x_is_pre_long_weekend__mutmut_30 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_31'] = x_is_pre_long_weekend__mutmut_31 # type: ignore # mutmut generated
mutants_x_is_pre_long_weekend__mutmut['x_is_pre_long_weekend__mutmut_32'] = x_is_pre_long_weekend__mutmut_32 # type: ignore # mutmut generated
