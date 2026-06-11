#!/usr/bin/env python3
"""§104 — FINRA daily short-sale volume direct downloader.

FINRA publishes daily short-sale volume files free at:
  https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files

Per-venue TRF/ADF files since 2009-08-03; consolidated NMS since 2018-08-01.
Published same evening (~6pm ET) → next-day-usable, PIT-clean.

This module downloads directly from FINRA (not via Polygon) to get the full
2009+ history needed for backtest validation.
"""

from __future__ import annotations

import io
import time
import logging
from datetime import date
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.finra_short_volume")

# FINRA daily short-sale volume URL template
# Date format in URL: MMDDYY (e.g., 080309 for 2009-08-03)
_FINRA_SV_URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{yymmdd}.txt"
# Consolidated NMS file prefix
_FINRA_CONSOLIDATED_PREFIX = "CNMS"

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_finra_short_volume"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "finra_short_volume_panel.pkl"

# Module-level in-memory cache
_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0


def _yymmdd(d: date) -> str:
    return d.strftime("%Y%m%d")


def _parse_finra_sv_txt(content: bytes) -> pd.DataFrame | None:
    """Parse a FINRA short-volume TXT file (pipe-delimited, with header)."""
    try:
        df = pd.read_csv(
            io.BytesIO(content),
            sep="|",
            header=0,
            dtype={
                "Date": str,
                "Symbol": str,
                "ShortVolume": "Int64",
                "ShortExemptVolume": "Int64",
                "TotalVolume": "Int64",
                "Market": str,
            },
        )
        df = df.rename(
            columns={
                "Date": "date",
                "Symbol": "symbol",
                "ShortVolume": "short_volume",
                "ShortExemptVolume": "short_exempt_volume",
                "TotalVolume": "total_volume",
                "Market": "market",
            }
        )
        df = df.assign(date=pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce").dt.date)
        df = df.dropna(subset=["date"])
        # The CNMS file already contains consolidated NMS data;
        # keep rows with valid symbols (some rows may have placeholder symbols).
        df = df[df["symbol"].notna() & (df["symbol"] != "")]
        return df
    except Exception as exc:
        log.warning(f"[finra_sv] parse error: {exc}")
        return None


async def download_finra_short_volume(
    d: date,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download FINRA short-volume for a single date. Never raises."""
    cache_key = f"sv_{d.isoformat()}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    cache_file = _CACHE_DIR / f"CNMSshvol{_yymmdd(d)}.txt"
    if cache_file.exists():
        try:
            df = _parse_finra_sv_txt(cache_file.read_bytes())
            if df is not None and not df.empty:
                _cache[cache_key] = (df, time.monotonic())
                return df
        except Exception:
            pass

    url = _FINRA_SV_URL.format(yymmdd=_yymmdd(d))
    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(url, timeout=30) as resp:
            if resp.status != 200:
                log.debug(f"[finra_sv] {d} HTTP {resp.status}")
                return None
            content = await resp.read()
            if not content:
                return None
            cache_file.write_bytes(content)
            df = _parse_finra_sv_txt(content)
            if df is not None and not df.empty:
                _cache[cache_key] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[finra_sv] {d} download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


def _compute_sv_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute short-volume ratio and 5d delta per ticker."""
    df = df.copy()
    df = df.assign(short_volume_ratio=(df["short_volume"] / df["total_volume"] * 100.0).where(df["total_volume"] > 0))
    df = df.sort_values(["symbol", "date"]).copy()
    df = df.assign(sv_ratio_5d_delta=df.groupby("symbol")["short_volume_ratio"].diff(5))
    return df


async def build_short_volume_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Batch backfill FINRA short-volume panel. Idempotent (skips existing files).

    If tickers is None, uses all tickers found in downloaded files.
    If start is None, defaults to 2009-08-03.
    If end is None, defaults to today.
    """
    if start is None:
        start = date(2009, 8, 3)
    if end is None:
        end = date.today()

    trading_dates = pd.bdate_range(start=start, end=end).date
    log.info(f"[finra_sv] backfill {len(trading_dates)} trading dates ({start} to {end})")

    frames: list[pd.DataFrame] = []
    for d in trading_dates:
        df = await download_finra_short_volume(d)
        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        log.warning("[finra_sv] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(frames, ignore_index=True)
    panel = _compute_sv_features(panel)

    if tickers:
        tickers_upper = [t.upper() for t in tickers]
        panel = panel[panel["symbol"].isin(tickers_upper)].copy()

    panel.rename(columns={"symbol": "ticker"}, inplace=True)
    panel.to_pickle(_PANEL_PATH)
    log.info(f"[finra_sv] panel saved: {len(panel)} rows → {_PANEL_PATH}")
    return panel


def load_short_volume_panel() -> pd.DataFrame | None:
    """Load cached panel if it exists."""
    if _PANEL_PATH.exists():
        return pd.read_pickle(_PANEL_PATH)
    return None


def merge_sv_pit(
    df: pd.DataFrame,
    sv_panel: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Merge FINRA short-volume into a ticker DataFrame with PIT discipline.

    FINRA publishes evening of trade date T → usable from T+1 open.
    We merge_asof with a 1-day backward look to enforce this.
    """
    if sv_panel.empty or "ticker" not in sv_panel.columns:
        df["sv_ratio"] = 0.0
        df["sv_ratio_5d_delta"] = 0.0
        return df

    sv = sv_panel[sv_panel["ticker"] == ticker.upper()][["date", "short_volume_ratio", "sv_ratio_5d_delta"]].copy()
    if sv.empty:
        df["sv_ratio"] = 0.0
        df["sv_ratio_5d_delta"] = 0.0
        return df

    sv = sv.assign(date=pd.to_datetime(sv["date"]))
    sv = sv.sort_values("date")

    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)
    df = pd.merge_asof(
        df.sort_values("_merge_date"),
        sv.rename(
            columns={
                "short_volume_ratio": "sv_ratio",
                "sv_ratio_5d_delta": "sv_ratio_5d_delta",
            }
        ),
        left_on="_merge_date",
        right_on="date",
        direction="backward",
    ).copy()
    df.drop(columns=["date", "_merge_date"], inplace=True, errors="ignore")
    df = df.assign(
        sv_ratio=df["sv_ratio"].fillna(0.0),
        sv_ratio_5d_delta=df["sv_ratio_5d_delta"].fillna(0.0),
    )
    return df
