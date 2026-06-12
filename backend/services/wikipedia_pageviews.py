#!/usr/bin/env python3
"""§109 — Wikipedia pageviews attention spike fetcher.

Wikimedia REST API: daily per-article views, free, clean.
  https://wikimedia.org/api/rest_v1/#/Pageviews%20data/get_metrics_pageviews_

Literature is mixed-to-positive on attention-based signals.
Hypothesis fit: pageview spike + oversold print = retail-visible panic
(the fear premium made measurable per-ticker).

Bounded test: company-page views for the IS universe, spike z-score at
entry as sizing context, 2015+ subperiod, per-fold.

PIT discipline: pageviews are published next-day → 1-day lag.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import date, timedelta
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.wikipedia_pageviews")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_wikipedia"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "wikipedia_pageviews_panel.parquet"
_PICKLE_PATH = _CACHE_DIR / "wikipedia_pageviews_panel.pkl"  # legacy

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0

# Wikimedia REST API endpoint
_WIKI_API = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "en.wikipedia/all-access/all-agents/{article}/daily/{start}/{end}"
)

# Ticker → Wikipedia article title mapping
_WIKI_ARTICLES: dict[str, str] = {
    "AAPL": "Apple_Inc.",
    "MSFT": "Microsoft",
    "AMZN": "Amazon_(company)",
    "GOOGL": "Google",
    "META": "Meta_Platforms",
    "TSLA": "Tesla,_Inc.",
    "NVDA": "Nvidia",
    "JPM": "JPMorgan_Chase",
    "V": "Visa_Inc.",
    "JNJ": "Johnson_&_Johnson",
    "UNH": "UnitedHealth_Group",
    "XOM": "ExxonMobil",
    "PG": "Procter_&_Gamble",
    "HD": "The_Home_Depot",
    "MA": "Mastercard",
    "ABBV": "AbbVie",
    "PFE": "Pfizer",
    "CVX": "Chevron_Corporation",
    "PEP": "PepsiCo",
    "LLY": "Eli_Lilly_and_Company",
}

_PILOT_TICKERS = os.getenv(
    "WIKI_PILOT_TICKERS",
    ",".join(_WIKI_ARTICLES.keys()),
).split(",")


def _parse_wiki_json(data: dict) -> pd.DataFrame | None:
    """Parse Wikimedia pageviews JSON."""
    try:
        items = data.get("items", [])
        if not items:
            return None
        rows = []
        for item in items:
            ts = item["timestamp"]
            views = item["views"]
            rows.append(
                {
                    "date": pd.to_datetime(ts, format="%Y%m%d%H").date(),
                    "views": int(views),
                }
            )
        df = pd.DataFrame(rows)
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except Exception as exc:
        log.warning(f"[wiki] parse error: {exc}")
        return None


async def download_wikipedia_pageviews(
    article: str,
    start: date,
    end: date,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download Wikipedia pageviews for a single article."""
    cache_key = f"wiki_{article}_{start.isoformat()}_{end.isoformat()}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    s = start.strftime("%Y%m%d")
    e = end.strftime("%Y%m%d")
    url = _WIKI_API.format(article=article, start=s, end=e)
    headers = {"User-Agent": "Signal.Trade Research Bot (signal@example.com)"}

    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(url, headers=headers, timeout=30) as resp:
            if resp.status != 200:
                log.debug(f"[wiki] {article} HTTP {resp.status}")
                return None
            data = await resp.json()
            df = _parse_wiki_json(data)
            if df is not None and not df.empty:
                _cache[cache_key] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[wiki] {article} download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


async def build_wikipedia_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Batch backfill Wikipedia pageviews panel."""
    if tickers is None:
        tickers = _PILOT_TICKERS
    if start is None:
        start = date(2015, 7, 1)  # API coverage starts ~2015-07
    if end is None:
        end = date.today()

    log.info(f"[wiki] backfill {len(tickers)} tickers ({start} to {end})")

    all_frames: list[pd.DataFrame] = []
    for ticker in tickers:
        article = _WIKI_ARTICLES.get(ticker.upper())
        if not article:
            log.debug(f"[wiki] no article for {ticker}")
            continue
        df = await download_wikipedia_pageviews(article, start, end)
        if df is not None and not df.empty:
            df = df.copy()
            # Compute 63d rolling z-score
            df = df.assign(
                views_63d_mean=df["views"].rolling(63, min_periods=21).mean(),
                views_63d_std=df["views"].rolling(63, min_periods=21).std(),
            )
            df = df.assign(
                views_z=((df["views"] - df["views_63d_mean"]) / df["views_63d_std"].replace(0, 1)).fillna(0.0),
                ticker=ticker.upper(),
            )
            all_frames.append(df)

    if not all_frames:
        log.warning("[wiki] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(all_frames, ignore_index=True)
    # Cross-sectional z-score within each date: how spiky is attention for a
    # ticker relative to the whole pilot universe on that day?
    panel = panel.assign(
        views_z_xs=panel.groupby("date")["views_z"].transform(
            lambda x: ((x - x.mean()) / x.std().replace(0, 1)).fillna(0.0)
        )
    )
    panel.to_parquet(_PANEL_PATH, index=False)
    if _PICKLE_PATH.exists():
        try:
            _PICKLE_PATH.unlink()
        except Exception:
            pass
    log.info(f"[wiki] panel saved: {len(panel)} rows → {_PANEL_PATH}")
    return panel


def load_wikipedia_panel() -> pd.DataFrame | None:
    if _PANEL_PATH.exists():
        return pd.read_parquet(_PANEL_PATH)
    if _PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_PICKLE_PATH)
            df.to_parquet(_PANEL_PATH, index=False)
            _PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning(f"[wiki] legacy pickle unloadable ({exc}); rebuild panel")
    return None


def merge_wikipedia_pit(
    df: pd.DataFrame,
    wiki_panel: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Merge Wikipedia pageviews into ticker DataFrame with 1-day PIT lag."""
    if wiki_panel.empty or "ticker" not in wiki_panel.columns:
        df["views"] = 0
        df["views_z"] = 0.0
        return df

    sub = wiki_panel[wiki_panel["ticker"] == ticker.upper()].copy()
    if sub.empty:
        df["views"] = 0
        df["views_z"] = 0.0
        return df

    sub = sub.assign(date=pd.to_datetime(sub["date"]) + timedelta(days=1))
    sub = sub.sort_values("date")

    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)
    df = pd.merge_asof(
        df.sort_values("_merge_date"),
        sub[["date", "views", "views_z"]],
        left_on="_merge_date",
        right_on="date",
        direction="backward",
    ).copy()
    df.drop(columns=["date", "_merge_date"], inplace=True, errors="ignore")
    df = df.assign(
        views=df["views"].fillna(0).astype(int),
        views_z=df["views_z"].fillna(0.0),
    )
    return df
