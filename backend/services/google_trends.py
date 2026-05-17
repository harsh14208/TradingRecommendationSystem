"""
Google Trends — rising search volume for a ticker signals retail FOMO.
Uses pytrends (free, no API key). Cached 6h per ticker.
"""
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=1)  # pytrends is not thread-safe at scale
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 21600  # 6 hours


def _fetch_trends(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent  = float(series.iloc[-1])           # last week
        prior   = float(series.iloc[-5:-1].mean()) # prior 4 weeks avg
        avg_3m  = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg     = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent":      recent,
            "prior_4w":    round(prior, 1),
            "avg_3m":      round(avg_3m, 1),
            "change_pct":  change_pct,
            "vs_avg_pct":  vs_avg,
            "signal":      signal,
            "score":       score,
        }
    except Exception as e:
        print(f"[trends] {ticker}: {e}")
        return {}


async def get_google_trends(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    if result:
        _cache[ticker] = (result, time.time())
    return result or {}
