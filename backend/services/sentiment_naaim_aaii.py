#!/usr/bin/env python3
"""§106 — Investor Sentiment fetchers (FRED UMCSENT + optional NAAIM/AAII).

Primary: FRED UMCSENT (University of Michigan Consumer Sentiment)
  - Monthly, since 1952, free via FRED API
  - Well-known contrarian washout marker
  - PIT: 2-week publication lag (survey month → mid-month release)

Optional fallbacks (require working external endpoints):
  NAAIM: actual manager equity exposure, weekly since 2006.
  AAII: bull/bear survey, weekly since 1987.

Both are classic contrarian washout markers — orthogonal to VIX level
(positioning vs implied vol).
"""

from __future__ import annotations

import io
import logging
import os
import time
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

# Load .env so FRED_API_KEY is available at module import time
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

log = logging.getLogger("signal.trade.sentiment_naaim_aaii")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_sentiment"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_UMCSENT_PANEL_PATH = _CACHE_DIR / "umcsent_panel.parquet"
_NAAIM_PANEL_PATH = _CACHE_DIR / "naaim_panel.parquet"
_AAII_PANEL_PATH = _CACHE_DIR / "aaii_panel.parquet"
_UMCSENT_PICKLE_PATH = _CACHE_DIR / "umcsent_panel.pkl"  # legacy
_NAAIM_PICKLE_PATH = _CACHE_DIR / "naaim_panel.pkl"  # legacy
_AAII_PICKLE_PATH = _CACHE_DIR / "aaii_panel.pkl"  # legacy

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 86400.0

_FRED_KEY = os.getenv("FRED_API_KEY")
_NAAIM_LANDING_URL = "https://naaim.org/programs/naaim-exposure-index/"
_NAAIM_XLSX_BASE = "https://naaim.org"
_AAII_URL = os.getenv(
    "AAII_DATA_URL",
    "https://www.aaii.com/files/surveys/sentiment.xls",
)


# ── FRED UMCSENT (primary, robust) ──────────────────────────────────────────


async def download_umcsent_panel(
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download UMCSENT from FRED API."""
    cached = _cache.get("umcsent")
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]
    if _UMCSENT_PANEL_PATH.exists():
        try:
            df = pd.read_parquet(_UMCSENT_PANEL_PATH)
            _cache["umcsent"] = (df, time.monotonic())
            return df
        except Exception:
            pass

    if not _FRED_KEY:
        log.warning("[umcsent] FRED_API_KEY not set")
        return None

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "UMCSENT",
        "api_key": _FRED_KEY,
        "file_type": "json",
        "observation_start": "2000-01-01",
    }
    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                log.warning(f"[umcsent] HTTP {resp.status}")
                return None
            data = await resp.json()
            obs = data.get("observations", [])
            rows = []
            for o in obs:
                v = o.get("value", ".")
                if v == ".":
                    continue
                rows.append(
                    {
                        "date": pd.to_datetime(o["date"]).date(),
                        "umcsent": float(v),
                    }
                )
            if not rows:
                return None
            df = pd.DataFrame(rows)
            df = df.sort_values("date").reset_index(drop=True)
            # 2-week publication lag: monthly survey released mid-next-month
            df = df.assign(date=df["date"] + pd.Timedelta(days=14))
            df.to_parquet(_UMCSENT_PANEL_PATH, index=False)
            _cache["umcsent"] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[umcsent] download error: {exc}")
        return None
    finally:
        if session is None and "_sess" in locals() and _sess is not None:
            await _sess.__aexit__(None, None, None)


# ── NAAIM (optional fallback) ───────────────────────────────────────────────


def _parse_naaim_xlsx(content: bytes) -> pd.DataFrame | None:
    """Parse NAAIM 'USE Data-since-Inception' xlsx."""
    try:
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        # Expected columns: Date, Mean/Average, Most Bearish Response, Quart 1, Quart 2, Quart 3, Most Bullish Response, Standard Deviation, NAAIM Number, S&P 500
        if "Date" not in df.columns or "Mean/Average" not in df.columns:
            log.warning("[naaim] unexpected xlsx columns")
            return None
        df = df.rename(columns={"Date": "date", "Mean/Average": "naaim_exposure"})
        df = df.assign(date=pd.to_datetime(df["date"]).dt.date)
        df = df.dropna(subset=["date", "naaim_exposure"])
        df = df.sort_values("date").reset_index(drop=True)
        # Deduplicate: some xlsx files have duplicate rows
        df = df.drop_duplicates(subset=["date"], keep="first")
        # PIT lag: weekly release on Wednesday → usable Thursday (1-day lag)
        df = df.assign(date=df["date"] + pd.Timedelta(days=1))
        return df[["date", "naaim_exposure"]]
    except Exception as exc:
        log.warning(f"[naaim] parse error: {exc}")
        return None


async def download_naaim_panel(
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download NAAIM exposure index full-history panel from naaim.org xlsx."""
    cached = _cache.get("naaim")
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]
    if _NAAIM_PANEL_PATH.exists():
        try:
            df = pd.read_parquet(_NAAIM_PANEL_PATH)
            _cache["naaim"] = (df, time.monotonic())
            return df
        except Exception:
            pass

    try:
        _sess = session or await shared_session().__aenter__()
        # Step 1: scrape landing page for current xlsx href
        async with _sess.get(_NAAIM_LANDING_URL, timeout=30) as resp:
            if resp.status != 200:
                log.debug(f"[naaim] landing HTTP {resp.status}")
                return None
            html = await resp.text()
            import re

            m = re.search(r'href="([^"]+USE_Data-since-Inception[^"]+\.xlsx)"', html)
            if not m:
                log.warning("[naaim] could not find xlsx href on landing page")
                return None
            xlsx_url = m.group(1)
            if xlsx_url.startswith("/"):
                xlsx_url = _NAAIM_XLSX_BASE + xlsx_url

        # Step 2: download xlsx
        async with _sess.get(xlsx_url, timeout=60) as resp:
            if resp.status != 200:
                log.debug(f"[naaim] xlsx HTTP {resp.status}")
                return None
            content = await resp.read()
            df = _parse_naaim_xlsx(content)
            if df is not None and not df.empty:
                df.to_parquet(_NAAIM_PANEL_PATH, index=False)
                _cache["naaim"] = (df, time.monotonic())
                log.info(f"[naaim] downloaded {len(df)} rows from {xlsx_url}")
            return df
    except Exception as exc:
        log.warning(f"[naaim] download error: {exc}")
        return None
    finally:
        if session is None and "_sess" in locals() and _sess is not None:
            await _sess.__aexit__(None, None, None)


# ── AAII (optional fallback) ────────────────────────────────────────────────


def _parse_aaii_xls(content: bytes) -> pd.DataFrame | None:
    """Parse AAII historical sentiment XLS."""
    try:
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl", skiprows=4)
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
            df = pd.read_parquet(_AAII_PANEL_PATH)
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
            # AAII endpoint often returns HTML block page instead of XLS
            if content[:5] == b"<!DOC":
                log.warning("[aaii] received HTML block page instead of XLS")
                return None
            df = _parse_aaii_xls(content)
            if df is not None and not df.empty:
                df.to_parquet(_AAII_PANEL_PATH, index=False)
                _cache["aaii"] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[aaii] download error: {exc}")
        return None
    finally:
        if session is None and "_sess" in locals() and _sess is not None:
            await _sess.__aexit__(None, None, None)


# ── Loaders (used by backtest / cross-sectional model) ──────────────────────


def load_umcsent_panel() -> pd.DataFrame | None:
    if _UMCSENT_PANEL_PATH.exists():
        return pd.read_parquet(_UMCSENT_PANEL_PATH)
    if _UMCSENT_PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_UMCSENT_PICKLE_PATH)
            df.to_parquet(_UMCSENT_PANEL_PATH, index=False)
            _UMCSENT_PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning(f"[umcsent] legacy pickle unloadable ({exc})")
    return None


def load_naaim_panel() -> pd.DataFrame | None:
    if _NAAIM_PANEL_PATH.exists():
        return pd.read_parquet(_NAAIM_PANEL_PATH)
    if _NAAIM_PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_NAAIM_PICKLE_PATH)
            df.to_parquet(_NAAIM_PANEL_PATH, index=False)
            _NAAIM_PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning(f"[naaim] legacy pickle unloadable ({exc})")
    return None


def load_aaii_panel() -> pd.DataFrame | None:
    if _AAII_PANEL_PATH.exists():
        return pd.read_parquet(_AAII_PANEL_PATH)
    if _AAII_PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_AAII_PICKLE_PATH)
            df.to_parquet(_AAII_PANEL_PATH, index=False)
            _AAII_PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning(f"[aaii] legacy pickle unloadable ({exc})")
    return None


# ── PIT merge ───────────────────────────────────────────────────────────────


def merge_sentiment_pit(
    df: pd.DataFrame,
    umcsent: pd.DataFrame | None = None,
    naaim: pd.DataFrame | None = None,
    aaii: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Merge sentiment features into ticker DataFrame with PIT lag."""
    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)

    if umcsent is not None and not umcsent.empty:
        umcsent = umcsent.assign(date=pd.to_datetime(umcsent["date"])).sort_values("date")
        df = pd.merge_asof(
            df.sort_values("_merge_date"),
            umcsent[["date", "umcsent"]],
            left_on="_merge_date",
            right_on="date",
            direction="backward",
        ).copy()
        df.drop(columns=["date"], inplace=True, errors="ignore")
        df = df.assign(umcsent=df["umcsent"].ffill())
    else:
        df = df.assign(umcsent=pd.NA)

    if naaim is not None and not naaim.empty:
        naaim = naaim.assign(date=pd.to_datetime(naaim["date"])).sort_values("date")
        df = pd.merge_asof(
            df.sort_values("_merge_date"),
            naaim[["date", "naaim_exposure"]],
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
