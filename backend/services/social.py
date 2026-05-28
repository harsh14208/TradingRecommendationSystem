"""
Social sentiment signals — StockTwits + Reddit WSB mention velocity.
Both use free public APIs (no key required).
Cached per ticker: 30 minutes.
"""

import ssl
import time
from urllib.parse import quote

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 1800  # 30 minutes

_HEADERS = {"User-Agent": "SignalTrade/1.0 research@signal.trade"}


async def get_social_sentiment(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    messages = d.get("messages", [])
                    bull = sum(
                        1
                        for m in messages
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "Bullish"
                    )
                    bear = sum(
                        1
                        for m in messages
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            print(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            print(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result
