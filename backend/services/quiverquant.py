"""
Congressional trading signals from Quiverquant (free tier, no key needed).
Uses the bulk endpoint and filters by ticker — the per-ticker endpoint returns 404.
Bulk data is cached 4 hours; per-ticker results are cached 24 hours.
"""
import ssl
import time
import asyncio
from datetime import datetime, timedelta

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_ticker_cache: dict[str, tuple[dict, float]] = {}
_bulk_cache:   dict = {"data": None, "ts": 0.0}

TICKER_TTL = 86400      # 24h per ticker
BULK_TTL   = 14400      # 4h for the bulk fetch

_URL  = "https://api.quiverquant.com/beta/live/congresstrading"
_HDRS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


async def _fetch_bulk() -> list:
    now = time.time()
    if _bulk_cache["data"] is not None and now - _bulk_cache["ts"] < BULK_TTL:
        return _bulk_cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector, headers=_HDRS) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _bulk_cache["data"] or []
                data = await r.json(content_type=None)
        if isinstance(data, list):
            _bulk_cache["data"] = data
            _bulk_cache["ts"]   = now
            return data
    except Exception as e:
        print(f"[congress] bulk fetch: {e}")
    return _bulk_cache["data"] or []


async def get_congress_signal(ticker: str) -> dict:
    cached = _ticker_cache.get(ticker)
    if cached and time.time() - cached[1] < TICKER_TTL:
        return cached[0]

    try:
        all_trades = await _fetch_bulk()
        if not all_trades:
            return {}  # bulk fetch failed entirely — don't cache, try again next scan

        cutoff = datetime.utcnow() - timedelta(days=90)
        recent_buys, recent_sells = [], []

        for t in all_trades:
            if t.get("Ticker", "").upper() != ticker.upper():
                continue
            date_str = t.get("TransactionDate") or t.get("ReportDate") or ""
            try:
                txn_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                continue
            if txn_date < cutoff:
                continue
            txn = t.get("Transaction", "").lower()
            rep = t.get("Representative", "?")
            amt = t.get("Range", t.get("Amount", ""))
            entry = {"rep": rep, "amount": amt, "date": txn_date.strftime("%Y-%m-%d")}
            if "purchase" in txn or "buy" in txn:
                recent_buys.append(entry)
            elif "sale" in txn or "sell" in txn:
                recent_sells.append(entry)

        nb, ns = len(recent_buys), len(recent_sells)
        net = nb - ns

        if net >= 3:
            signal, score = "bullish",  8
        elif net >= 1:
            signal, score = "bullish",  4
        elif net <= -3:
            signal, score = "bearish", -8
        elif net <= -1:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral",  0

        result = {
            "buys":         nb,
            "sells":        ns,
            "net":          net,
            "signal":       signal,
            "score":        score,
            "recent_buys":  recent_buys[:3],
            "recent_sells": recent_sells[:3],
        }
        _ticker_cache[ticker] = (result, time.time())
        return result

    except Exception as e:
        print(f"[congress] {ticker}: {e}")
        return {}
