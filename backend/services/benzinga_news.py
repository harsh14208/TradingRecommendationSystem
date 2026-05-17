"""
Polygon.io News — Drop-in replacement for RSS scraper.

Uses Polygon.io v2/reference/news which is accessible on the free plan.
Returns structured news with publisher, tickers, and title — we score sentiment
ourselves using keyword matching (no pre-scored API sentiment field available
at this tier, but signal is still better than RSS due to latency <5min).

Latency vs RSS: ~2–5 minutes vs 15–30 minutes.
Cache: 5 minutes per ticker.
"""
import asyncio
import logging
import os
import ssl
import time
from datetime import datetime, timezone

import aiohttp
import certifi

log = logging.getLogger("signal.trade.polygon_news")

_cache: dict[str, dict] = {}
_TTL = 300  # 5-minute per-ticker cache
_BASE = "https://api.polygon.io/v2/reference/news"

# Simple keyword-based sentiment scoring
_BULL_WORDS = {
    "beat", "beats", "record", "surge", "soars", "rises", "gain", "profit",
    "revenue", "growth", "strong", "upgrade", "buy", "bullish", "outperform",
    "raised", "raises", "guidance", "exceeds", "acquisition", "buyback",
    "dividend", "partnership", "deal", "approved", "expansion",
}
_BEAR_WORDS = {
    "miss", "misses", "cut", "cuts", "falls", "drops", "decline", "loss",
    "warning", "downgrade", "sell", "bearish", "underperform", "layoff",
    "recall", "lawsuit", "investigation", "fraud", "debt", "bankruptcy",
    "guidance", "below", "disappoints", "withdraws", "delays",
}


def _score_headline(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def _age_decay(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:   return 1.0
        if age_h < 8:   return 0.7
        if age_h < 24:  return 0.4
        return 0.15
    except Exception:
        return 0.5


async def get_benzinga_news(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc",
              "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx,
                                   timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub  = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay    = _age_decay(pub)
        articles.append({
            "headline":     a.get("title", ""),
            "sentiment":    round(raw_sent * decay, 3),
            "raw_sentiment": round(raw_sent, 3),
            "url":          a.get("article_url", ""),
            "published_at": pub,
            "source":       (a.get("publisher") or {}).get("name", "News"),
            "age_decay":    round(decay, 2),
        })

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


def score_benzinga_news(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:   return +4.0, headline, "Bullish"
    if net >= 0.1:   return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:  return -4.0, headline, "Bearish"
    if net <= -0.1:  return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


async def get_benzinga_news_score(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


# ── Batch news fetch — 154 tickers in 1-2 paginated API calls ──────────────
# v2/reference/news without ticker filter returns latest 50 articles across ALL tickers.
# Indexing by `tickers` array covers ~20-30 watchlist tickers per page.
# Replaces 154 individual calls (~35s) with 2-3 paginated calls (~5s).

_batch_cache: dict = {"data": {}, "ts": 0.0}
_BATCH_TTL = 600  # 10 minutes


async def prefetch_news_batch(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with aiohttp.ClientSession() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50, "order": "desc",
                    "sort": "published_utc", "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(_BASE, params=params, ssl=ssl_ctx,
                                       timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        break
                    data    = await resp.json()
                    raw     = data.get("results") or []
                    cursor  = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub  = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec  = _age_decay(pub)
                        art  = {
                            "headline":      a.get("title", ""),
                            "sentiment":     round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url":           a.get("article_url", ""),
                            "published_at":  pub,
                            "source":        (a.get("publisher") or {}).get("name", "News"),
                            "age_decay":     round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"]   = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers "
             f"in 3 API calls (was 154)")
