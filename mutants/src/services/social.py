"""
Social sentiment signals — StockTwits + Reddit WSB mention velocity.
Both use free public APIs (no key required).
Cached per ticker: 30 minutes.
"""

import logging
import ssl
import time
from urllib.parse import quote

log = logging.getLogger("signal.trade.social")

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 1800  # 30 minutes

_HEADERS = {"User-Agent": "SignalTrade/1.0 research@signal.trade"}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_social_sentiment__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_social_sentiment__mutmut)
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_orig(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_1(ticker: str) -> dict:
    cached = None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_2(ticker: str) -> dict:
    cached = _cache.get(None)
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_3(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached or time.time() - cached[1] < CACHE_TTL:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_4(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() + cached[1] < CACHE_TTL:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_5(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[2] < CACHE_TTL:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_6(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] <= CACHE_TTL:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_7(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[1]

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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_8(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_9(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = None

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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_10(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=None)

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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_11(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=None, headers=_HEADERS) as session:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_12(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=None) as session:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_13(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(headers=_HEADERS) as session:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_14(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, ) as session:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_15(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_16(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(None, timeout=aiohttp.ClientTimeout(total=8)) as r:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_17(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(url, timeout=None) as r:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_18(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(timeout=aiohttp.ClientTimeout(total=8)) as r:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_19(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(url, ) as r:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_20(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=None)) as r:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_21(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    result: dict = {}
    connector = aiohttp.TCPConnector(ssl=_ssl_ctx)

    async with aiohttp.ClientSession(connector=connector, headers=_HEADERS) as session:
        # ── StockTwits ────────────────────────────────────────────────────
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=9)) as r:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_22(ticker: str) -> dict:
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
                if r.status != 200:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_23(ticker: str) -> dict:
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
                if r.status == 201:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_24(ticker: str) -> dict:
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
                    d = None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_25(ticker: str) -> dict:
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
                    messages = None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_26(ticker: str) -> dict:
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
                    messages = d.get(None, [])
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_27(ticker: str) -> dict:
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
                    messages = d.get("messages", None)
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_28(ticker: str) -> dict:
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
                    messages = d.get([])
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_29(ticker: str) -> dict:
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
                    messages = d.get("messages", )
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_30(ticker: str) -> dict:
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
                    messages = d.get("XXmessagesXX", [])
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_31(ticker: str) -> dict:
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
                    messages = d.get("MESSAGES", [])
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_32(ticker: str) -> dict:
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
                    bull = None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_33(ticker: str) -> dict:
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
                        None
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_34(ticker: str) -> dict:
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
                        2
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_35(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get(None) == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_36(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) and {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_37(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get(None, {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_38(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", None) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_39(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get({}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_40(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", ) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_41(ticker: str) -> dict:
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
                        if (m.get(None, {}).get("sentiment", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_42(ticker: str) -> dict:
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
                        if (m.get("entities", None).get("sentiment", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_43(ticker: str) -> dict:
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
                        if (m.get({}).get("sentiment", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_44(ticker: str) -> dict:
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
                        if (m.get("entities", ).get("sentiment", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_45(ticker: str) -> dict:
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
                        if (m.get("XXentitiesXX", {}).get("sentiment", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_46(ticker: str) -> dict:
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
                        if (m.get("ENTITIES", {}).get("sentiment", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_47(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("XXsentimentXX", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_48(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("SENTIMENT", {}) or {}).get("basic") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_49(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("XXbasicXX") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_50(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("BASIC") == "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_51(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") != "Bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_52(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "XXBullishXX"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_53(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "bullish"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_54(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "BULLISH"
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_55(ticker: str) -> dict:
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
                    bear = None
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_56(ticker: str) -> dict:
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
                        None
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_57(ticker: str) -> dict:
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
                        2
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_58(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get(None) == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_59(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) and {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_60(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get(None, {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_61(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", None) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_62(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get({}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_63(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", ) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_64(ticker: str) -> dict:
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
                        if (m.get(None, {}).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_65(ticker: str) -> dict:
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
                        if (m.get("entities", None).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_66(ticker: str) -> dict:
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
                        if (m.get({}).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_67(ticker: str) -> dict:
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
                        if (m.get("entities", ).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_68(ticker: str) -> dict:
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
                        if (m.get("XXentitiesXX", {}).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_69(ticker: str) -> dict:
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
                        if (m.get("ENTITIES", {}).get("sentiment", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_70(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("XXsentimentXX", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_71(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("SENTIMENT", {}) or {}).get("basic") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_72(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("XXbasicXX") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_73(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("BASIC") == "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_74(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") != "Bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_75(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "XXBearishXX"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_76(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "bearish"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_77(ticker: str) -> dict:
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
                        if (m.get("entities", {}).get("sentiment", {}) or {}).get("basic") == "BEARISH"
                    )
                    total = bull + bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_78(ticker: str) -> dict:
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
                    total = None
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_79(ticker: str) -> dict:
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
                    total = bull - bear
                    if total > 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_80(ticker: str) -> dict:
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
                    if total >= 0:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_81(ticker: str) -> dict:
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
                    if total > 1:
                        bull_pct = round(bull / total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_82(ticker: str) -> dict:
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
                        bull_pct = None
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_83(ticker: str) -> dict:
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
                        bull_pct = round(None, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_84(ticker: str) -> dict:
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
                        bull_pct = round(bull / total * 100, None)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_85(ticker: str) -> dict:
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
                        bull_pct = round(1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_86(ticker: str) -> dict:
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
                        bull_pct = round(bull / total * 100, )
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_87(ticker: str) -> dict:
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
                        bull_pct = round(bull / total / 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_88(ticker: str) -> dict:
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
                        bull_pct = round(bull * total * 100, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_89(ticker: str) -> dict:
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
                        bull_pct = round(bull / total * 101, 1)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_90(ticker: str) -> dict:
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
                        bull_pct = round(bull / total * 100, 2)
                        result["st_bull_pct"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_91(ticker: str) -> dict:
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
                        result["st_bull_pct"] = None
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_92(ticker: str) -> dict:
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
                        result["XXst_bull_pctXX"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_93(ticker: str) -> dict:
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
                        result["ST_BULL_PCT"] = bull_pct
                        result["st_total"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_94(ticker: str) -> dict:
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
                        result["st_total"] = None
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_95(ticker: str) -> dict:
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
                        result["XXst_totalXX"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_96(ticker: str) -> dict:
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
                        result["ST_TOTAL"] = len(messages)
                        result["st_bull"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_97(ticker: str) -> dict:
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
                        result["st_bull"] = None
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_98(ticker: str) -> dict:
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
                        result["XXst_bullXX"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_99(ticker: str) -> dict:
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
                        result["ST_BULL"] = bull
                        result["st_bear"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_100(ticker: str) -> dict:
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
                        result["st_bear"] = None
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_101(ticker: str) -> dict:
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
                        result["XXst_bearXX"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_102(ticker: str) -> dict:
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
                        result["ST_BEAR"] = bear
        except Exception as e:
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_103(ticker: str) -> dict:
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
            log.warning(None)

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_104(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = None
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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_105(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(None)}&sort=new&t=week&limit=100"
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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_106(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(None, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_107(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=None) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_108(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_109(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, ) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_110(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=None)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_111(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=9)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_112(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status != 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_113(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 201:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_114(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = None
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_115(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = None
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_116(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get(None, [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_117(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", None)
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_118(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get([])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_119(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", )
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_120(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get(None, {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_121(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", None).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_122(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get({}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_123(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", ).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_124(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("XXdataXX", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_125(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("DATA", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_126(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("XXchildrenXX", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_127(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("CHILDREN", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_128(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = None
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_129(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["XXwsb_mentions_7dXX"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_130(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["WSB_MENTIONS_7D"] = len(posts)
                    # Also check 1-day recent
                    now_ts = time.time()
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_131(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

        # ── Reddit WSB mention velocity ───────────────────────────────────
        try:
            url = f"https://www.reddit.com/r/wallstreetbets/search.json?q={quote(ticker)}&sort=new&t=week&limit=100"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    d = await r.json(content_type=None)
                    posts = d.get("data", {}).get("children", [])
                    result["wsb_mentions_7d"] = len(posts)
                    # Also check 1-day recent
                    now_ts = None
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_132(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = None
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_133(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts + p.get("data", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_134(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get(None, 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_135(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", None) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_136(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get(0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_137(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", ) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_138(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get(None, {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_139(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", None).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_140(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get({}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_141(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", ).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_142(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("XXdataXX", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_143(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("DATA", {}).get("created_utc", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_144(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("XXcreated_utcXX", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_145(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("CREATED_UTC", 0) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_146(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 1) < 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_147(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) <= 86400]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_148(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    day_posts = [p for p in posts if now_ts - p.get("data", {}).get("created_utc", 0) < 86401]
                    result["wsb_mentions_1d"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_149(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    result["wsb_mentions_1d"] = None
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_150(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    result["XXwsb_mentions_1dXX"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_151(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
                    result["WSB_MENTIONS_1D"] = len(day_posts)
        except Exception as e:
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_152(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(None)

    _cache[ticker] = (result, time.time())
    return result


async def x_get_social_sentiment__mutmut_153(ticker: str) -> dict:
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
            log.warning(f"[social] StockTwits {ticker}: {e}")

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
            log.warning(f"[social] Reddit {ticker}: {e}")

    _cache[ticker] = None
    return result

mutants_x_get_social_sentiment__mutmut['_mutmut_orig'] = x_get_social_sentiment__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_1'] = x_get_social_sentiment__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_2'] = x_get_social_sentiment__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_3'] = x_get_social_sentiment__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_4'] = x_get_social_sentiment__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_5'] = x_get_social_sentiment__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_6'] = x_get_social_sentiment__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_7'] = x_get_social_sentiment__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_8'] = x_get_social_sentiment__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_9'] = x_get_social_sentiment__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_10'] = x_get_social_sentiment__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_11'] = x_get_social_sentiment__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_12'] = x_get_social_sentiment__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_13'] = x_get_social_sentiment__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_14'] = x_get_social_sentiment__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_15'] = x_get_social_sentiment__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_16'] = x_get_social_sentiment__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_17'] = x_get_social_sentiment__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_18'] = x_get_social_sentiment__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_19'] = x_get_social_sentiment__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_20'] = x_get_social_sentiment__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_21'] = x_get_social_sentiment__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_22'] = x_get_social_sentiment__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_23'] = x_get_social_sentiment__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_24'] = x_get_social_sentiment__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_25'] = x_get_social_sentiment__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_26'] = x_get_social_sentiment__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_27'] = x_get_social_sentiment__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_28'] = x_get_social_sentiment__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_29'] = x_get_social_sentiment__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_30'] = x_get_social_sentiment__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_31'] = x_get_social_sentiment__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_32'] = x_get_social_sentiment__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_33'] = x_get_social_sentiment__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_34'] = x_get_social_sentiment__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_35'] = x_get_social_sentiment__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_36'] = x_get_social_sentiment__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_37'] = x_get_social_sentiment__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_38'] = x_get_social_sentiment__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_39'] = x_get_social_sentiment__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_40'] = x_get_social_sentiment__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_41'] = x_get_social_sentiment__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_42'] = x_get_social_sentiment__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_43'] = x_get_social_sentiment__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_44'] = x_get_social_sentiment__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_45'] = x_get_social_sentiment__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_46'] = x_get_social_sentiment__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_47'] = x_get_social_sentiment__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_48'] = x_get_social_sentiment__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_49'] = x_get_social_sentiment__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_50'] = x_get_social_sentiment__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_51'] = x_get_social_sentiment__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_52'] = x_get_social_sentiment__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_53'] = x_get_social_sentiment__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_54'] = x_get_social_sentiment__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_55'] = x_get_social_sentiment__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_56'] = x_get_social_sentiment__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_57'] = x_get_social_sentiment__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_58'] = x_get_social_sentiment__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_59'] = x_get_social_sentiment__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_60'] = x_get_social_sentiment__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_61'] = x_get_social_sentiment__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_62'] = x_get_social_sentiment__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_63'] = x_get_social_sentiment__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_64'] = x_get_social_sentiment__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_65'] = x_get_social_sentiment__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_66'] = x_get_social_sentiment__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_67'] = x_get_social_sentiment__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_68'] = x_get_social_sentiment__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_69'] = x_get_social_sentiment__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_70'] = x_get_social_sentiment__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_71'] = x_get_social_sentiment__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_72'] = x_get_social_sentiment__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_73'] = x_get_social_sentiment__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_74'] = x_get_social_sentiment__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_75'] = x_get_social_sentiment__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_76'] = x_get_social_sentiment__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_77'] = x_get_social_sentiment__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_78'] = x_get_social_sentiment__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_79'] = x_get_social_sentiment__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_80'] = x_get_social_sentiment__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_81'] = x_get_social_sentiment__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_82'] = x_get_social_sentiment__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_83'] = x_get_social_sentiment__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_84'] = x_get_social_sentiment__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_85'] = x_get_social_sentiment__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_86'] = x_get_social_sentiment__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_87'] = x_get_social_sentiment__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_88'] = x_get_social_sentiment__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_89'] = x_get_social_sentiment__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_90'] = x_get_social_sentiment__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_91'] = x_get_social_sentiment__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_92'] = x_get_social_sentiment__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_93'] = x_get_social_sentiment__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_94'] = x_get_social_sentiment__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_95'] = x_get_social_sentiment__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_96'] = x_get_social_sentiment__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_97'] = x_get_social_sentiment__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_98'] = x_get_social_sentiment__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_99'] = x_get_social_sentiment__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_100'] = x_get_social_sentiment__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_101'] = x_get_social_sentiment__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_102'] = x_get_social_sentiment__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_103'] = x_get_social_sentiment__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_104'] = x_get_social_sentiment__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_105'] = x_get_social_sentiment__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_106'] = x_get_social_sentiment__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_107'] = x_get_social_sentiment__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_108'] = x_get_social_sentiment__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_109'] = x_get_social_sentiment__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_110'] = x_get_social_sentiment__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_111'] = x_get_social_sentiment__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_112'] = x_get_social_sentiment__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_113'] = x_get_social_sentiment__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_114'] = x_get_social_sentiment__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_115'] = x_get_social_sentiment__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_116'] = x_get_social_sentiment__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_117'] = x_get_social_sentiment__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_118'] = x_get_social_sentiment__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_119'] = x_get_social_sentiment__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_120'] = x_get_social_sentiment__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_121'] = x_get_social_sentiment__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_122'] = x_get_social_sentiment__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_123'] = x_get_social_sentiment__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_124'] = x_get_social_sentiment__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_125'] = x_get_social_sentiment__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_126'] = x_get_social_sentiment__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_127'] = x_get_social_sentiment__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_128'] = x_get_social_sentiment__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_129'] = x_get_social_sentiment__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_130'] = x_get_social_sentiment__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_131'] = x_get_social_sentiment__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_132'] = x_get_social_sentiment__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_133'] = x_get_social_sentiment__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_134'] = x_get_social_sentiment__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_135'] = x_get_social_sentiment__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_136'] = x_get_social_sentiment__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_137'] = x_get_social_sentiment__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_138'] = x_get_social_sentiment__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_139'] = x_get_social_sentiment__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_140'] = x_get_social_sentiment__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_141'] = x_get_social_sentiment__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_142'] = x_get_social_sentiment__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_143'] = x_get_social_sentiment__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_144'] = x_get_social_sentiment__mutmut_144 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_145'] = x_get_social_sentiment__mutmut_145 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_146'] = x_get_social_sentiment__mutmut_146 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_147'] = x_get_social_sentiment__mutmut_147 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_148'] = x_get_social_sentiment__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_149'] = x_get_social_sentiment__mutmut_149 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_150'] = x_get_social_sentiment__mutmut_150 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_151'] = x_get_social_sentiment__mutmut_151 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_152'] = x_get_social_sentiment__mutmut_152 # type: ignore # mutmut generated
mutants_x_get_social_sentiment__mutmut['x_get_social_sentiment__mutmut_153'] = x_get_social_sentiment__mutmut_153 # type: ignore # mutmut generated
