import asyncio
import ssl
import time
from typing import Optional

import aiohttp
import certifi

from services.redis_cache import cache_get, cache_set

_cache:   dict = {"data": None, "ts": 0.0}  # in-process fallback for serve-stale-on-error
_ssl_ctx: ssl.SSLContext = ssl.create_default_context(cafile=certifi.where())
CACHE_TTL = 3600  # refresh once per hour
_CACHE_KEY = "fear_greed:data"

URL         = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
_REFERER    = "https://www.cnn.com/markets/fear-and-greed"
_HEADERS    = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer":         _REFERER,
    "Origin":          "https://www.cnn.com",
    "DNT":             "1",
    "Connection":      "keep-alive",
    "Sec-Fetch-Dest":  "empty",
    "Sec-Fetch-Mode":  "cors",
    "Sec-Fetch-Site":  "same-site",
}

# (lo, hi) → (label, sentiment for rationale, confidence_bias)
_BANDS = [
    (0,  25,  "Extreme Fear",  "pos", +15),  # contrarian: oversold market = buy dip
    (25, 45,  "Fear",          "pos",  +7),
    (45, 55,  "Neutral",       "neu",   0),
    (55, 75,  "Greed",         "neg",  -5),
    (75, 101, "Extreme Greed", "neg", -13),  # complacency = top risk
]


def _classify(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "Neutral", "neu", 0


def _neutral_result() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score":          round(score, 1),
        "label":          label,
        "sentiment":      sentiment,
        "score_bias":     bias,
        "prev_close":     round(score, 1),
        "prev_1w":        round(score, 1),
        "prev_1m":        round(score, 1),
    }


async def get_fear_greed() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    print(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score":          round(score, 1),
            "label":          label,
            "sentiment":      sentiment,
            "score_bias":     bias,
            "prev_close":     round(float(fg.get("previous_close",   score)), 1),
            "prev_1w":        round(float(fg.get("previous_1_week",  score)), 1),
            "prev_1m":        round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"]   = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        print(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


import csv, io as _io
_pc_cache: dict = {"ratio": None, "ts": 0.0}

async def get_put_call_ratio() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time, aiohttp, ssl, certifi
    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = ssl.create_default_context(cafile=certifi.where())
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio":    round(ratio, 3),
                        "signal":   "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias":     10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"]    = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None
