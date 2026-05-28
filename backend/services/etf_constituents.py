"""
ETF Constituents — Massive Partners API

Maps sector ETFs to their top holdings. When an ETF has strong fund flows,
the score is amplified for its top-10 holdings (vs smaller constituents).

Weight tiers:
  Top 3 holdings  (≥ 8% weight each) → flow score × 1.5
  Holdings 4–10   (3–8% weight)      → flow score × 1.0
  Holdings 11–30  (<3% weight)       → flow score × 0.5
  Remaining       (tail)             → no amplification

Also used to identify when a stock is at risk of ETF rebalancing
(quarterly → known inclusion/exclusion dates).

Cache: 24 hours (ETF composition changes quarterly).
"""

import asyncio
import logging
import os
import time

import aiohttp

log = logging.getLogger("signal.trade.etf_constituents")

_cache: dict[str, dict] = {}
_TTL = 86400  # 24 hours

_BASE = "https://api.polygon.io"

TRACKED_ETFS = ["XLK", "XLF", "XLY", "XLC", "XLV", "XLP", "XLE", "XLI", "XLB", "XLRE", "XLU", "QQQ", "SPY", "IWM"]


async def _fetch_constituents(etf: str, api_key: str) -> list[dict]:
    import ssl

    import certifi

    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    # Polygon.io ETF constituents — requires Starter plan or higher
    url = f"{_BASE}/v3/reference/tickers?type=ETF&market=stocks&apiKey={api_key}&search={etf}&limit=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:  # 403 = premium — return empty, SECTOR_MAP fallback used
                    return []
                data = await resp.json()
                return data.get("results") or []
    except Exception:
        return []


async def get_etf_constituents(etf: str) -> list[dict]:
    """Return top-50 constituents for an ETF. 24h cache."""
    now = time.time()
    if etf in _cache and now - _cache[etf]["ts"] < _TTL:
        return _cache[etf]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    raw = await _fetch_constituents(etf, api_key)
    constituents = []
    for row in raw:
        ticker = (row.get("ticker") or row.get("symbol") or "").upper()
        weight = float(row.get("weight") or row.get("weight_pct") or 0)
        if ticker:
            constituents.append({"ticker": ticker, "weight": round(weight, 4)})
    constituents.sort(key=lambda x: x["weight"], reverse=True)

    _cache[etf] = {"data": constituents, "ts": now}
    return constituents


async def preload_all() -> dict[str, list[dict]]:
    """Fetch constituents for all tracked ETFs concurrently."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}
    results = await asyncio.gather(*[get_etf_constituents(e) for e in TRACKED_ETFS], return_exceptions=True)
    return {etf: (r if isinstance(r, list) else []) for etf, r in zip(TRACKED_ETFS, results)}


def get_constituent_weight(ticker: str, etf: str) -> float:
    """Return the weight (0.0–1.0) of a ticker in a given ETF. Uses cache only."""
    cached = _cache.get(etf, {}).get("data") or []
    for c in cached:
        if c["ticker"] == ticker:
            return c["weight"]
    return 0.0


def get_flow_amplifier(ticker: str, etf: str) -> float:
    """
    Return a flow amplification multiplier based on ETF constituency weight.
    Top 3 holdings: 1.5×; holdings 4-10: 1.0×; 11-30: 0.5×; else: 0.0.
    """
    cached = _cache.get(etf, {}).get("data") or []
    for rank, c in enumerate(cached, start=1):
        if c["ticker"] == ticker:
            if rank <= 3:
                return 1.5
            if rank <= 10:
                return 1.0
            if rank <= 30:
                return 0.5
            return 0.0
    return 0.0
