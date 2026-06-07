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
