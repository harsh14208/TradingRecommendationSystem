import time
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

_executor = ThreadPoolExecutor(max_workers=2)
_cache: dict[str, tuple[list, float]] = {}
_rec_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 900  # 15 minutes
REC_CACHE_TTL = 3600  # analyst recs change slowly

# Finnhub API call tracker (rolling 60s window, free tier = 60/min)
_call_times: deque = deque()

def _track_call():
    now = time.time()
    _call_times.append(now)
    # Prune older than 60s
    while _call_times and now - _call_times[0] > 60:
        _call_times.popleft()

def get_api_usage() -> dict:
    now = time.time()
    while _call_times and now - _call_times[0] > 60:
        _call_times.popleft()
    used = len(_call_times)
    return {"used_last_60s": used, "limit": 60, "pct": round(used / 60 * 100)}

POSITIVE_WORDS = {
    "beat", "beats", "surpass", "surpasses", "strong", "growth", "upgrade",
    "bullish", "record", "rally", "gain", "profit", "revenue", "raise", "buy",
    "outperform", "expand", "breakthrough", "exceed", "exceeds", "positive",
    "upside", "boom", "soar", "soars", "jump", "jumps", "surge", "surges",
}
NEGATIVE_WORDS = {
    "miss", "misses", "decline", "loss", "downgrade", "bearish", "cut",
    "concern", "risk", "investigation", "lawsuit", "weak", "disappointing",
    "fall", "falls", "drop", "drops", "sell", "underperform", "warning",
    "negative", "below", "slump", "slumps", "crash", "crashes", "layoff",
}


def score_sentiment(text: str) -> float:
    words = set(text.lower().split())
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 2)


def _fetch_news(ticker: str, days: int) -> list[dict]:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    try:
        import finnhub
        from config import get_settings
        settings = get_settings()
        if not settings.finnhub_api_key:
            return []

        client = finnhub.Client(api_key=settings.finnhub_api_key)
        _track_call()
        to_dt = datetime.now()
        from_dt = to_dt - timedelta(days=days)
        raw = client.company_news(
            ticker,
            _from=from_dt.strftime("%Y-%m-%d"),
            to=to_dt.strftime("%Y-%m-%d"),
        )
        result = raw[:10] if raw else []
        _cache[ticker] = (result, time.time())
        return result
    except Exception:
        return []


def _fetch_analyst_recs(ticker: str) -> dict:
    """Return latest Finnhub analyst consensus + month-over-month revision momentum."""
    cached = _rec_cache.get(ticker)
    if cached and time.time() - cached[1] < REC_CACHE_TTL:
        return cached[0]
    try:
        import finnhub
        from config import get_settings
        settings = get_settings()
        if not settings.finnhub_api_key:
            return {}
        client = finnhub.Client(api_key=settings.finnhub_api_key)
        _track_call()
        raw = client.recommendation_trends(ticker)
        if not raw:
            return {}
        # Most recent period is first; index 1 is prior month
        latest = raw[0]
        result = {
            "period":      latest.get("period", ""),
            "strong_buy":  latest.get("strongBuy",  0),
            "buy":         latest.get("buy",        0),
            "hold":        latest.get("hold",       0),
            "sell":        latest.get("sell",       0),
            "strong_sell": latest.get("strongSell", 0),
        }

        # ── Revision momentum: current month vs prior month ──────────────
        # bull_score = strongBuy*2 + buy (weights conviction)
        # bear_score = strongSell*2 + sell
        if len(raw) >= 2:
            prior = raw[1]
            cur_bull  = latest.get("strongBuy", 0) * 2 + latest.get("buy", 0)
            prior_bull = prior.get("strongBuy", 0) * 2  + prior.get("buy", 0)
            cur_bear  = latest.get("strongSell", 0) * 2 + latest.get("sell", 0)
            prior_bear = prior.get("strongSell", 0) * 2  + prior.get("sell", 0)
            bull_delta = cur_bull  - prior_bull
            bear_delta = cur_bear  - prior_bear

            # Revision score: +ve = analysts upgrading, -ve = downgrading
            # Cap at ±8 to avoid outsized effect from thin analyst coverage
            rev_pts = max(-8, min(8, bull_delta - bear_delta))
            result["revision_pts"]    = rev_pts
            result["revision_period"] = prior.get("period", "")
            result["bull_delta"]      = bull_delta
            result["bear_delta"]      = bear_delta

        # ── 12-1 month momentum factor from Finnhub basic_financials ─────────
        # Uses pre-computed price returns (free endpoint, same API key).
        # 26-week return minus 4-week return approximates the documented
        # 12-month minus 1-month cross-sectional momentum factor (skip recent month
        # to avoid short-term reversal). Strong positive momentum persists.
        try:
            _track_call()
            _bf = client.company_basic_financials(ticker, "all")
            _m  = (_bf or {}).get("metric", {})
            _r13 = _m.get("13WeekPriceReturnDaily")   # ~3-month return
            _r26 = _m.get("26WeekPriceReturnDaily")   # ~6-month return
            _r52 = _m.get("52WeekHigh")
            _l52 = _m.get("52WeekLow")
            if _r13 is not None and _r26 is not None:
                # Momentum ≈ 26w return minus short-term 4w noise (approximated as r13/3)
                _mom = round(float(_r26) - float(_r13) / 3.0, 2)
                result["momentum_factor"] = _mom
                result["return_26w"]      = round(float(_r26), 2)
                result["return_13w"]      = round(float(_r13), 2)
            if _r52 is not None:
                result["fh_52w_high"] = float(_r52)
            if _l52 is not None:
                result["fh_52w_low"]  = float(_l52)
        except Exception:
            pass

        _rec_cache[ticker] = (result, time.time())
        return result
    except Exception:
        return {}


async def get_analyst_recs(ticker: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_analyst_recs, ticker)


async def get_company_news(ticker: str, days: int = 7) -> list[dict]:
    raw = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_news, ticker, days)

    items = []
    for item in raw[:6]:
        headline = item.get("headline", "")
        summary = item.get("summary", headline)
        ts = item.get("datetime", 0)
        hours_ago = max(0, int((time.time() - ts) / 3600)) if ts else 0
        items.append({
            "headline": headline,
            "summary": summary[:300] if summary else headline,
            "sentiment": score_sentiment(headline + " " + summary),
            "hours_ago": hours_ago,
            "source": item.get("source", "Finnhub"),
            "url": item.get("url", ""),
        })
    return items
