#!/usr/bin/env python3
"""§107 — GDELT news tone fetcher (bounded pilot).

GDELT is 100% free (raw files + BigQuery), archives to 1979, GKG 2.0 with
per-org tone from 2015. Entity→ticker mapping is the hard part.

Pilot is bounded: 20 IS tickers × 2015+, company-name match in GKG
organizations, daily tone z-score panel.

Question: does negative-news-tone-at-oversold-entry predict the bounce
(capitulation) or the knife (repricing)? Either answer recalibrates a live
family that currently runs on faith.

PIT discipline: GDELT publishes next-day for global events; we lag by 1 day.
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import zipfile
from datetime import date, timedelta
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.gdelt_news_tone")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_gdelt"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "gdelt_tone_panel.parquet"
_PICKLE_PATH = _CACHE_DIR / "gdelt_tone_panel.pkl"  # legacy

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0

# GDELT GKG 1.0 daily files (one per calendar day), available 2015+.
_GDELT_GKG_PREFIX = "http://data.gdeltproject.org/gkg/"

# Bounded pilot: company-name → ticker mapping for 20 IS tickers
_PILOT_TICKERS = os.getenv(
    "GDELT_PILOT_TICKERS",
    "AAPL,MSFT,AMZN,GOOGL,META,TSLA,NVDA,JPM,V,JNJ,UNH,XOM,PG,HD,MA,ABBV,PFE,CVX,PEP,LLY",
).split(",")

_COMPANY_NAMES: dict[str, list[str]] = {
    "AAPL": ["Apple Inc", "Apple"],
    "MSFT": ["Microsoft Corp", "Microsoft"],
    "AMZN": ["Amazon.com Inc", "Amazon"],
    "GOOGL": ["Alphabet Inc", "Google", "Alphabet"],
    "META": ["Meta Platforms Inc", "Facebook", "Meta"],
    "TSLA": ["Tesla Inc", "Tesla"],
    "NVDA": ["NVIDIA Corp", "NVIDIA"],
    "JPM": ["JPMorgan Chase", "JPMorgan"],
    "V": ["Visa Inc", "Visa"],
    "JNJ": ["Johnson & Johnson", "J&J"],
    "UNH": ["UnitedHealth Group", "UnitedHealth"],
    "XOM": ["Exxon Mobil Corp", "Exxon"],
    "PG": ["Procter & Gamble", "P&G"],
    "HD": ["Home Depot Inc", "Home Depot"],
    "MA": ["Mastercard Inc", "Mastercard"],
    "ABBV": ["AbbVie Inc", "AbbVie"],
    "PFE": ["Pfizer Inc", "Pfizer"],
    "CVX": ["Chevron Corp", "Chevron"],
    "PEP": ["PepsiCo Inc", "PepsiCo"],
    "LLY": ["Eli Lilly and Co", "Eli Lilly"],
}


def _parse_gkg_csv(content: bytes) -> pd.DataFrame | None:
    """Parse a GDELT GKG 1.0 daily CSV (tab-delimited, zip archive).

    GKG 1.0 columns (daily):
      0=DATE, 1=NUMARTS, 2=COUNTS, 3=THEMES, 4=LOCATIONS, 5=PERSONS,
      6=ORGANIZATIONS, 7=TONE, ...
    """
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not names:
                return None
            with zf.open(names[0]) as csv_file:
                df = pd.read_csv(
                    csv_file,
                    sep="\t",
                    header=None,
                    dtype=str,
                    low_memory=False,
                    skiprows=1,
                )
        if df.shape[1] < 8:
            return None
        df = df.iloc[:, [0, 6, 7]].copy()
        df.columns = ["date", "organizations", "tone"]
        df = df.assign(date=pd.to_datetime(df["date"], format="%Y%m%d").dt.date)
        return df
    except Exception as exc:
        log.warning("[gdelt] parse error: %s", exc)
        return None


def _extract_org_tone(df: pd.DataFrame, ticker: str) -> pd.DataFrame | None:
    """Extract tone rows matching a ticker's company names."""
    names = _COMPANY_NAMES.get(ticker.upper(), [ticker.upper()])
    mask = df["organizations"].fillna("").str.contains("|".join(names), case=False, na=False)
    sub = df[mask].copy()
    if sub.empty:
        return None
    # Tone format: "tone,pos,neg,polarity,activity,SELFREF"
    tone_parts = sub["tone"].str.split(",", expand=True)
    if tone_parts.shape[1] < 1:
        return None
    sub = sub.assign(tone_score=pd.to_numeric(tone_parts[0], errors="coerce"))
    sub = sub.dropna(subset=["tone_score"])
    if sub.empty:
        return None
    return sub[["date", "tone_score"]]


async def download_gdelt_gkg(
    d: date,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download GDELT GKG for a single date."""
    yyyymmdd = d.strftime("%Y%m%d")
    url = f"{_GDELT_GKG_PREFIX}{yyyymmdd}.gkg.csv.zip"
    cache_file = _CACHE_DIR / f"{yyyymmdd}.gkg.csv.zip"

    if cache_file.exists():
        try:
            return _parse_gkg_csv(cache_file.read_bytes())
        except Exception:
            pass

    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(url, timeout=120) as resp:
            if resp.status != 200:
                log.debug(f"[gdelt] {d} HTTP {resp.status}")
                return None
            content = await resp.read()
            if not content:
                return None
            cache_file.write_bytes(content)
            return _parse_gkg_csv(content)
    except Exception as exc:
        log.warning(f"[gdelt] {d} download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


async def _download_gdelt_one(
    d: date,
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> tuple[date, pd.DataFrame | None]:
    async with semaphore:
        df = await download_gdelt_gkg(d, session=session)
    return d, df


async def build_gdelt_tone_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
    max_concurrency: int = 8,
    chunk_size: int = 50,
) -> pd.DataFrame:
    """Batch backfill GDELT tone panel (bounded pilot).

    Downloads GKG zip files concurrently in chunks to keep memory bounded and to
    emit progress logs. Uses a dedicated session with explicit total/connect
    timeouts so a single stalled request cannot hang the whole backfill.
    """
    if tickers is None:
        tickers = _PILOT_TICKERS
    if start is None:
        start = date(2015, 1, 1)
    if end is None:
        end = date.today()

    dates = pd.date_range(start=start, end=end, freq="D").date
    log.info("[gdelt] backfill %s days (%s to %s), tickers=%s", len(dates), start, end, tickers)

    timeout = aiohttp.ClientTimeout(total=180, connect=30)
    async with aiohttp.ClientSession(timeout=timeout) as _sess:
        semaphore = asyncio.Semaphore(max_concurrency)
        all_frames: list[pd.DataFrame] = []
        total_rows = 0
        for chunk_start in range(0, len(dates), chunk_size):
            chunk = dates[chunk_start : chunk_start + chunk_size]
            tasks = [_download_gdelt_one(d, _sess, semaphore) for d in chunk]
            results = await asyncio.gather(*tasks)
            for _d, df in results:
                if df is None or df.empty:
                    continue
                for ticker in tickers:
                    sub = _extract_org_tone(df, ticker)
                    if sub is not None and not sub.empty:
                        sub = sub.groupby("date")["tone_score"].agg(["mean", "std", "count"]).reset_index()
                        sub["ticker"] = ticker.upper()
                        sub.rename(
                            columns={"mean": "tone_mean", "std": "tone_std", "count": "tone_n"},
                            inplace=True,
                        )
                        sub["tone_z"] = (sub["tone_mean"] / sub["tone_std"].replace(0, 1)).fillna(0.0)
                        all_frames.append(sub)
                        total_rows += len(sub)
            if (chunk_start // chunk_size + 1) % 2 == 0 or chunk_start + chunk_size >= len(dates):
                log.info(
                    "[gdelt] processed %s/%s days, %s ticker-day rows so far",
                    min(chunk_start + chunk_size, len(dates)),
                    len(dates),
                    total_rows,
                )

    if not all_frames:
        log.warning("[gdelt] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(all_frames, ignore_index=True)
    panel.to_parquet(_PANEL_PATH, index=False)
    if _PICKLE_PATH.exists():
        try:
            _PICKLE_PATH.unlink()
        except Exception:
            pass
    log.info("[gdelt] panel saved: %s rows → %s", len(panel), _PANEL_PATH)
    return panel


def load_gdelt_tone_panel() -> pd.DataFrame | None:
    if _PANEL_PATH.exists():
        return pd.read_parquet(_PANEL_PATH)
    if _PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_PICKLE_PATH)
            df.to_parquet(_PANEL_PATH, index=False)
            _PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning(f"[gdelt] legacy pickle unloadable ({exc}); rebuild panel")
    return None


def merge_gdelt_tone_pit(
    df: pd.DataFrame,
    gdelt_panel: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Merge GDELT tone into ticker DataFrame with 1-day PIT lag."""
    if gdelt_panel.empty or "ticker" not in gdelt_panel.columns:
        df["tone_mean"] = 0.0
        df["tone_z"] = 0.0
        return df

    sub = gdelt_panel[gdelt_panel["ticker"] == ticker.upper()].copy()
    if sub.empty:
        df["tone_mean"] = 0.0
        df["tone_z"] = 0.0
        return df

    sub = sub.assign(date=pd.to_datetime(sub["date"]) + timedelta(days=1))  # 1-day lag
    sub = sub.sort_values("date")

    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)
    df = pd.merge_asof(
        df.sort_values("_merge_date"),
        sub[["date", "tone_mean", "tone_std"]],
        left_on="_merge_date",
        right_on="date",
        direction="backward",
    ).copy()
    df.drop(columns=["date", "_merge_date"], inplace=True, errors="ignore")
    df = df.assign(
        tone_mean=df["tone_mean"].fillna(0.0),
        tone_z=(df["tone_mean"] / df["tone_std"].replace(0, 1)).fillna(0.0),
    )
    return df
