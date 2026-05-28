"""
Corporate Events — Polygon.io reference endpoints.

Sources:
  v3/reference/dividends  — ex-dividend dates (bullish pre-event bid)
  v3/reference/splits     — stock splits (accessibility + retail attention)
  v2/reference/news       — detect M&A, earnings, guidance mentions in recent headlines

Signal value:
  Ex-dividend ≤ 2 days away     → +2 pts (support bid, dividend capture flow)
  Stock split ≤ 7 days away     → +2 pts (retail attention + accessibility)
  M&A news detected in headline → +6 pts / −4 pts (merger/takeover vs divestiture)
  Earnings guidance headline    → ±4 pts (raise/cut language)

4-hour cache per batch.
"""

import asyncio
import logging
import os
import ssl
import time
from datetime import date, timedelta

import aiohttp
import certifi

log = logging.getLogger("signal.trade.corporate_events")

_cache: dict = {"events": None, "by_ticker": None, "ts": 0.0}
_TTL = 3600  # 1 hour — ex-div/split dates via Polygon (unlimited calls)
_BASE = "https://api.polygon.io"

_MA_KEYWORDS = {"acqui", "merger", "takeover", "buyout", "acquisition", "acquire"}
_DIV_KEYWORDS = {"divestiture", "spinoff", "spin-off", "divest"}
_RAISE_KEYWORDS = {
    "raises guidance",
    "raised guidance",
    "raised outlook",
    "above expectations",
    "beat estimates",
    "beats estimates",
    "record revenue",
    "record earnings",
}
_CUT_KEYWORDS = {
    "cuts guidance",
    "cut guidance",
    "lowered outlook",
    "below expectations",
    "missed estimates",
    "misses estimates",
    "warning",
    "profit warning",
}


async def _fetch_dividends(tickers: list[str], ssl_ctx, api_key: str) -> list[dict]:
    today = date.today()
    end_date = (today + timedelta(days=7)).isoformat()
    events = []
    async with aiohttp.ClientSession() as session:

        async def fetch_one(ticker):
            url = f"{_BASE}/v3/reference/dividends"
            params = {
                "ticker": ticker,
                "ex_dividend_date.gte": today.isoformat(),
                "ex_dividend_date.lte": end_date,
                "limit": 3,
                "apiKey": api_key,
            }
            try:
                async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status != 200:
                        return
                    data = await resp.json()
                    for r in data.get("results") or []:
                        ex_date = r.get("ex_dividend_date", "")
                        if not ex_date:
                            continue
                        try:
                            days_away = (date.fromisoformat(ex_date) - today).days
                        except ValueError:
                            continue
                        events.append(
                            {
                                "ticker": ticker,
                                "type": "ExDividendDate",
                                "label": f"Ex-Dividend ${r.get('cash_amount', 0):.3f}",
                                "date": ex_date,
                                "days_away": days_away,
                                "signal_pts": 2 if days_away <= 2 else 0,
                                "within_window": days_away <= 2,
                            }
                        )
            except Exception:
                pass

        await asyncio.gather(*[fetch_one(t) for t in tickers])
    return events


async def _fetch_splits(tickers: list[str], ssl_ctx, api_key: str) -> list[dict]:
    today = date.today()
    end_date = (today + timedelta(days=14)).isoformat()
    events = []
    async with aiohttp.ClientSession() as session:

        async def fetch_one(ticker):
            url = f"{_BASE}/v3/reference/splits"
            params = {
                "ticker": ticker,
                "execution_date.gte": today.isoformat(),
                "execution_date.lte": end_date,
                "limit": 2,
                "apiKey": api_key,
            }
            try:
                async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status != 200:
                        return
                    data = await resp.json()
                    for r in data.get("results") or []:
                        ex_date = r.get("execution_date", "")
                        if not ex_date:
                            continue
                        try:
                            days_away = (date.fromisoformat(ex_date) - today).days
                        except ValueError:
                            continue
                        ratio = f"{r.get('split_from', 1)}:{r.get('split_to', 1)}"
                        events.append(
                            {
                                "ticker": ticker,
                                "type": "StockSplit",
                                "label": f"Stock Split {ratio}",
                                "date": ex_date,
                                "days_away": days_away,
                                "signal_pts": 2 if days_away <= 7 else 0,
                                "within_window": days_away <= 7,
                            }
                        )
            except Exception:
                pass

        await asyncio.gather(*[fetch_one(t) for t in tickers])
    return events


async def _fetch_news_events(tickers: list[str], ssl_ctx, api_key: str) -> list[dict]:
    """Detect M&A, guidance raise/cut from recent news headlines."""
    today = date.today().isoformat()
    events = []
    async with aiohttp.ClientSession() as session:

        async def fetch_one(ticker):
            url = f"{_BASE}/v2/reference/news"
            params = {
                "ticker": ticker,
                "limit": 5,
                "order": "desc",
                "sort": "published_utc",
                "published_utc.gte": today,
                "apiKey": api_key,
            }
            try:
                async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status != 200:
                        return
                    data = await resp.json()
                    for art in data.get("results") or []:
                        title = (art.get("title") or "").lower()
                        if any(k in title for k in _MA_KEYWORDS):
                            events.append(
                                {
                                    "ticker": ticker,
                                    "type": "MaterialAgreement",
                                    "label": "M&A / Acquisition news",
                                    "date": today,
                                    "days_away": 0,
                                    "signal_pts": 6,
                                    "within_window": True,
                                }
                            )
                            break
                        if any(k in title for k in _RAISE_KEYWORDS):
                            events.append(
                                {
                                    "ticker": ticker,
                                    "type": "GuidanceRaise",
                                    "label": "Guidance / earnings beat signal",
                                    "date": today,
                                    "days_away": 0,
                                    "signal_pts": 4,
                                    "within_window": True,
                                }
                            )
                            break
                        if any(k in title for k in _CUT_KEYWORDS):
                            events.append(
                                {
                                    "ticker": ticker,
                                    "type": "GuidanceCut",
                                    "label": "Guidance cut / earnings miss signal",
                                    "date": today,
                                    "days_away": 0,
                                    "signal_pts": -4,
                                    "within_window": True,
                                }
                            )
                            break
            except Exception:
                pass

        await asyncio.gather(*[fetch_one(t) for t in tickers])
    return events


async def get_corporate_events(tickers: list[str] | None = None) -> dict:
    """
    Public entrypoint. Fetches dividends + splits + news events for all tickers.
    Returns {"events": list, "by_ticker": dict}. 4-hour cache.
    """
    global _cache
    now = time.time()
    if _cache["events"] is not None and now - _cache["ts"] < _TTL:
        return {"events": _cache["events"], "by_ticker": _cache["by_ticker"]}

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"events": [], "by_ticker": {}}

    if not tickers:
        # Use a representative subset — fetching 154 tickers in parallel is fine
        from config import get_settings

        tickers = get_settings().tickers[:50]  # top 50 to keep startup fast

    ssl_ctx = ssl.create_default_context(cafile=certifi.where())

    divs, splits, news_ev = await asyncio.gather(
        _fetch_dividends(tickers, ssl_ctx, api_key),
        _fetch_splits(tickers, ssl_ctx, api_key),
        _fetch_news_events(tickers, ssl_ctx, api_key),
        return_exceptions=True,
    )

    all_events: list[dict] = []
    for batch in (divs, splits, news_ev):
        if isinstance(batch, list):
            all_events.extend(batch)

    all_events.sort(key=lambda e: e["date"])

    by_ticker: dict[str, list[dict]] = {}
    for ev in all_events:
        by_ticker.setdefault(ev["ticker"], []).append(ev)

    _cache["events"] = all_events
    _cache["by_ticker"] = by_ticker
    _cache["ts"] = now
    log.info(f"[corp_events] {len(all_events)} events for {len(by_ticker)} tickers")
    return {"events": all_events, "by_ticker": by_ticker}


def get_exdiv_blackout(ticker: str, events_ctx: dict | None) -> tuple[bool, str]:
    """
    Returns (True, label) when today IS the ex-dividend date for the ticker.
    On ex-date the stock price mechanically drops by the dividend amount —
    technical breakout/momentum signals are invalidated by this guaranteed drop.
    A hard HOLD avoids Supertrend / moving-average false-positives on ex-date.
    """
    if not events_ctx:
        return False, ""
    for ev in (events_ctx.get("by_ticker") or {}).get(ticker, []):
        if ev.get("type") == "ExDividendDate" and ev.get("days_away") == 0:
            return True, ev.get("label", "Ex-Dividend Date")
    return False, ""


def get_event_score(ticker: str, events_ctx: dict | None) -> tuple[float, list[str]]:
    """Return (score_pts, reasons) for signal_engine. Cap ±8."""
    if not events_ctx:
        return 0.0, []
    by_ticker = events_ctx.get("by_ticker", {})
    total, reasons = 0.0, []
    for ev in by_ticker.get(ticker, []):
        pts = ev.get("signal_pts", 0)
        if pts and ev.get("within_window"):
            total += pts
            reasons.append(f"{ev['label']} ({ev['date']}, +{ev['days_away']}d)")
    return (min(max(total, -8.0), 8.0), reasons)
