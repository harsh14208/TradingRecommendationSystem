#!/usr/bin/env python3
"""§106 — NAAIM Exposure Index + AAII Sentiment Survey fetchers.

NAAIM: actual manager equity exposure, weekly since 2006.
  https://en.macromicro.me/charts/46198/naaim-exposure-index
  (or official NAAIM site for raw data)

AAII: bull/bear survey, weekly since 1987.
  https://www.aaii.com/sentimentsurvey/sent_results

Both are classic contrarian washout markers — orthogonal to VIX level
(positioning vs implied vol). Lag to release day (Wed/Thu) in the join.

PIT discipline: join with release-day lag (Wed/Thu of survey week).
"""

from __future__ import annotations

import io
import logging
import time
import os
from pathlib import Path

import aiohttp
import pandas as pd

from backend.services.http_client import shared_session

log = logging.getLogger("signal.trade.sentiment_naaim_aaii")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_sentiment"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_NAAIM_PANEL_PATH = _CACHE_DIR / "naaim_panel.pkl"
_AAII_PANEL_PATH = _CACHE_DIR / "aaii_panel.pkl"

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 86400.0

# NAAIM publishes full history as a downloadable CSV on some mirrors;
# fallback: macromicro.me has a chart API; we use a public data source.
_NAAIM_URL = os.getenv(
    "NAAIM_DATA_URL",
    "https://en.macromicro.me/charts/data/46198",  # JSON endpoint for NAAIM
)
_AAII_URL = os.getenv(
    "AAII_DATA_URL",
    "https://www.aaii.com/files/surveys/sentiment.xls",  # Historical XLS
)


def _parse_naaim_json(data: dict) -> pd.DataFrame | None:
    """Parse NAAIM JSON from macromicro chart endpoint."""
    try:
        series = data.get("data", {}).get("series", [])
        if not series:
            return None
        rows = []
        for point in series[0].get("data", []):
            ts = point[0]
            val = point[1]
            rows.append({"date": pd.to_datetime(ts, unit="ms").date(), "naaim_exposure": float(val)})
        df = pd.DataFrame(rows)
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except Exception as exc:
        log.warning(f"[naaim] parse error: {exc}")
        return None


async def download_naaim_panel(
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download NAAIM exposure index full-history panel."""
    cached = _cache.get("naaim")
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]
    if _NAAIM_PANEL_PATH.exists():
        try:
            df = pd.read_pickle(_NAAIM_PANEL_PATH)
            _cache["naaim"] = (df, time.monotonic())
            return df
        except Exception:
            pass

    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(_NAAIM_URL, timeout=30) as resp:
            if resp.status != 200:
                log.debug(f"[naaim] HTTP {resp.status}")
                return None
            data = await resp.json()
            df = _parse_naaim_json(data)
            if df is not None and not df.empty:
                df.to_pickle(_NAAIM_PANEL_PATH)
                _cache["naaim"] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[naaim] download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


def _parse_aaii_xls(content: bytes) -> pd.DataFrame | None:
    """Parse AAII historical sentiment XLS."""
    try:
        df = pd.read_excel(io.BytesIO(content), skiprows=4)
        # Expected columns after skip: Date, Bullish, Neutral, Bearish, etc.
        df = df.rename(
            columns={
                "Date": "date",
                "Bullish": "aaii_bullish",
                "Neutral": "aaii_neutral",
                "Bearish": "aaii_bearish",
            }
        )
        df = df.assign(
            date=pd.to_datetime(df["date"]).dt.date,
            aaii_bull_bear_spread=df["aaii_bullish"] - df["aaii_bearish"],
        )
        df = df.dropna(subset=["date"])
        return df[["date", "aaii_bullish", "aaii_neutral", "aaii_bearish", "aaii_bull_bear_spread"]]
    except Exception as exc:
        log.warning(f"[aaii] parse error: {exc}")
        return None


async def download_aaii_panel(
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download AAII sentiment survey full-history panel."""
    cached = _cache.get("aaii")
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]
    if _AAII_PANEL_PATH.exists():
        try:
            df = pd.read_pickle(_AAII_PANEL_PATH)
            _cache["aaii"] = (df, time.monotonic())
            return df
        except Exception:
            pass

    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(_AAII_URL, timeout=60) as resp:
            if resp.status != 200:
                log.debug(f"[aaii] HTTP {resp.status}")
                return None
            content = await resp.read()
            df = _parse_aaii_xls(content)
            if df is not None and not df.empty:
                df.to_pickle(_AAII_PANEL_PATH)
                _cache["aaii"] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[aaii] download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


def load_naaim_panel() -> pd.DataFrame | None:
    if _NAAIM_PANEL_PATH.exists():
        return pd.read_pickle(_NAAIM_PANEL_PATH)
    return None


def load_aaii_panel() -> pd.DataFrame | None:
    if _AAII_PANEL_PATH.exists():
        return pd.read_pickle(_AAII_PANEL_PATH)
    return None


def merge_sentiment_pit(
    df: pd.DataFrame,
    naaim: pd.DataFrame | None,
    aaii: pd.DataFrame | None,
) -> pd.DataFrame:
    """Merge NAAIM + AAII into a ticker DataFrame with PIT discipline.

    Both publish Wed/Thu of the survey week. We merge_asof backward
    to ensure we only use released data.
    """
    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)

    if naaim is not None and not naaim.empty:
        naaim = naaim.assign(date=pd.to_datetime(naaim["date"])).sort_values("date")
        df = pd.merge_asof(
            df.sort_values("_merge_date"),
            naaim,
            left_on="_merge_date",
            right_on="date",
            direction="backward",
        ).copy()
        df.drop(columns=["date"], inplace=True, errors="ignore")
        df = df.assign(naaim_exposure=df["naaim_exposure"].fillna(50.0))
    else:
        df = df.assign(naaim_exposure=50.0)

    if aaii is not None and not aaii.empty:
        aaii = aaii.assign(date=pd.to_datetime(aaii["date"])).sort_values("date")
        df = pd.merge_asof(
            df.sort_values("_merge_date"),
            aaii,
            left_on="_merge_date",
            right_on="date",
            direction="backward",
        ).copy()
        df.drop(columns=["date"], inplace=True, errors="ignore")
        for col in ["aaii_bullish", "aaii_bearish", "aaii_bull_bear_spread"]:
            if col in df.columns:
                df = df.assign(**{col: df[col].fillna(0.0)})
    else:
        df = df.assign(aaii_bullish=0.0, aaii_bearish=0.0, aaii_bull_bear_spread=0.0)

    df.drop(columns=["_merge_date"], inplace=True, errors="ignore")
    return df
