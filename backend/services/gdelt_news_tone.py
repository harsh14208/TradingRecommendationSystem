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

import gzip
import io
import logging
import os
from datetime import date, timedelta
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.gdelt_news_tone")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_gdelt"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "gdelt_tone_panel.pkl"

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0

# GDELT GKG 2.0 daily master file list
_GDELT_MASTER_LIST = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
_GDELT_GKG_PREFIX = "http://data.gdeltproject.org/gdeltv2/"

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
    """Parse a GDELT GKG 2.0 CSV (tab-delimited, gzip)."""
    try:
        df = pd.read_csv(
            gzip.GzipFile(fileobj=io.BytesIO(content)),
            sep="\t",
            header=None,
            dtype=str,
            low_memory=False,
        )
        # GKG columns: 0=GKGRECORDID, 1=DATE, 2=SourceCollectionIdentifier,
        # 3=SourceCommonName, 4=DocumentIdentifier, 5=Counts, 6=V2Counts,
        # 7=Themes, 8=V2Themes, 9=Locations, 10=V2Locations,
        # 11=Persons, 12=V2Persons, 13=Organizations, 14=V2Organizations,
        # 15=V2Tone, ...
        if df.shape[1] < 16:
            return None
        df = df.iloc[:, [1, 13, 15]].copy()
        df.columns = ["date", "organizations", "tone"]
        df = df.assign(date=pd.to_datetime(df["date"], format="%Y%m%d%H%M%S").dt.date)
        return df
    except Exception as exc:
        log.warning(f"[gdelt] parse error: {exc}")
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


async def build_gdelt_tone_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Batch backfill GDELT tone panel (bounded pilot)."""
    if tickers is None:
        tickers = _PILOT_TICKERS
    if start is None:
        start = date(2015, 1, 1)
    if end is None:
        end = date.today()

    dates = pd.date_range(start=start, end=end, freq="D").date
    log.info(f"[gdelt] backfill {len(dates)} days ({start} to {end}), tickers={tickers}")

    all_frames: list[pd.DataFrame] = []
    for d in dates:
        df = await download_gdelt_gkg(d)
        if df is None or df.empty:
            continue
        for ticker in tickers:
            sub = _extract_org_tone(df, ticker)
            if sub is not None and not sub.empty:
                sub = sub.groupby("date")["tone_score"].agg(["mean", "std", "count"]).reset_index()
                sub["ticker"] = ticker.upper()
                sub.rename(columns={"mean": "tone_mean", "std": "tone_std", "count": "tone_n"}, inplace=True)
                all_frames.append(sub)

    if not all_frames:
        log.warning("[gdelt] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(all_frames, ignore_index=True)
    panel.to_pickle(_PANEL_PATH)
    log.info(f"[gdelt] panel saved: {len(panel)} rows → {_PANEL_PATH}")
    return panel


def load_gdelt_tone_panel() -> pd.DataFrame | None:
    if _PANEL_PATH.exists():
        return pd.read_pickle(_PANEL_PATH)
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
