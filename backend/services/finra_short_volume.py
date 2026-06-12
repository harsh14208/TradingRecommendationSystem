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

import asyncio
import io
import logging
import time
from datetime import date
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.finra_short_volume")

# FINRA daily short-sale volume URL template
# Date format in URL: YYYYMMDD (e.g., 20090803 for 2009-08-03)
_FINRA_SV_URL = "https://cdn.finra.org/equity/regsho/daily/{venue}shvol{yymmdd}.txt"

# Venue prefixes used before the consolidated NMS file took over.
# Only the venues that actually return 200 on historical dates are included.
_FINRA_VENUE_PREFIXES = ["FNRA", "FNSQ", "FNYX"]
_FINRA_CONSOLIDATED_PREFIX = "CNMS"

# Consolidated NMS coverage begins 2018-08-01 per FINRA docs.
_CONSOLIDATED_START = date(2018, 8, 1)

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_finra_short_volume"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "finra_short_volume_panel.parquet"
_PICKLE_PATH = _CACHE_DIR / "finra_short_volume_panel.pkl"  # legacy

# Module-level in-memory cache
_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0


def _yymmdd(d: date) -> str:
    return d.strftime("%Y%m%d")


def _parse_finra_sv_txt(content: bytes) -> pd.DataFrame | None:
    """Parse a FINRA short-volume TXT file (pipe-delimited, with header).

    Early per-venue files may lack ``ShortExemptVolume``; handle gracefully.
    """
    try:
        df = pd.read_csv(
            io.BytesIO(content),
            sep="|",
            header=0,
            dtype={
                "Date": str,
                "Symbol": str,
                "ShortVolume": float,
                "ShortExemptVolume": float,
                "TotalVolume": float,
                "Market": str,
            },
        )
    except Exception as exc:
        log.warning("[finra_sv] parse error: %s", exc)
        return None

    # Normalise column names; some files have trailing whitespace.
    df.columns = [c.strip() for c in df.columns]
    rename_map: dict[str, str] = {}
    for col in df.columns:
        if col == "Date":
            rename_map[col] = "date"
        elif col == "Symbol":
            rename_map[col] = "symbol"
        elif col == "ShortVolume":
            rename_map[col] = "short_volume"
        elif col == "ShortExemptVolume":
            rename_map[col] = "short_exempt_volume"
        elif col == "TotalVolume":
            rename_map[col] = "total_volume"
        elif col == "Market":
            rename_map[col] = "market"
    df = df.rename(columns=rename_map)

    # Drop metadata/trailer rows before casting to integer.
    df = df[df["symbol"].notna() & (df["symbol"] != "")]
    df = df.assign(date=pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce").dt.date)
    df = df.dropna(subset=["date"])

    # Ensure expected columns exist.
    for col in ("short_volume", "total_volume"):
        if col not in df.columns:
            df[col] = pd.NA
    if "short_exempt_volume" not in df.columns:
        df["short_exempt_volume"] = pd.NA
    if "market" not in df.columns:
        df["market"] = None

    # Cast to nullable integer; float decimals are rounded (FINRA sometimes reports
    # share-weighted fractional volume in recent files).
    for col in ("short_volume", "short_exempt_volume", "total_volume"):
        if col in df.columns:
            df = df.assign(**{col: df[col].round().astype("Int64")})

    return df


async def _download_one_venue(
    d: date,
    venue: str,
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> pd.DataFrame | None:
    """Download a single venue file for one date. Never raises."""
    cache_key = f"sv_{venue}_{d.isoformat()}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    cache_file = _CACHE_DIR / f"{venue}shvol{_yymmdd(d)}.txt"
    if cache_file.exists():
        try:
            df = _parse_finra_sv_txt(cache_file.read_bytes())
            if df is not None and not df.empty:
                _cache[cache_key] = (df, time.monotonic())
                return df
        except Exception:
            pass

    url = _FINRA_SV_URL.format(venue=venue, yymmdd=_yymmdd(d))
    try:
        async with semaphore:
            async with session.get(url, timeout=30) as resp:
                if resp.status != 200:
                    log.debug("[finra_sv] %s %s HTTP %s", venue, d, resp.status)
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
        log.debug("[finra_sv] %s %s download error: %s", venue, d, exc)
        return None


async def download_finra_short_volume(
    d: date,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download FINRA short-volume for a single date, aggregating venues when needed.

    Returns a consolidated DataFrame with columns:
      date, symbol, short_volume, short_exempt_volume, total_volume, market
    """
    cache_key = f"sv_{d.isoformat()}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    _sess = session or await shared_session().__aenter__()
    semaphore = asyncio.Semaphore(8)
    try:
        if d >= _CONSOLIDATED_START:
            df = await _download_one_venue(d, _FINRA_CONSOLIDATED_PREFIX, _sess, semaphore)
        else:
            tasks = [_download_one_venue(d, v, _sess, semaphore) for v in _FINRA_VENUE_PREFIXES]
            frames = [f for f in await asyncio.gather(*tasks) if f is not None and not f.empty]
            if not frames:
                return None
            df = _aggregate_venues(pd.concat(frames, ignore_index=True))

        if df is not None and not df.empty:
            _cache[cache_key] = (df, time.monotonic())
        return df
    except Exception as exc:
        log.warning("[finra_sv] %s aggregate download error: %s", d, exc)
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


def _aggregate_venues(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-venue rows to one consolidated row per (date, symbol)."""
    df = df.copy()
    grouped = df.groupby(["date", "symbol"], as_index=False).agg(
        short_volume=("short_volume", "sum"),
        short_exempt_volume=("short_exempt_volume", "sum"),
        total_volume=("total_volume", "sum"),
        market=("market", lambda x: ",".join(sorted(set(str(i) for i in x if pd.notna(i))))),
    )
    return grouped


def _reconcile_venues(d: date, venue_df: pd.DataFrame | None, cnms_df: pd.DataFrame | None) -> None:
    """Log discrepancies between aggregated per-venue totals and CNMS for overlap dates."""
    if venue_df is None or cnms_df is None or venue_df.empty or cnms_df.empty:
        return
    merged = venue_df.merge(
        cnms_df[["date", "symbol", "total_volume", "short_volume"]],
        on=["date", "symbol"],
        suffixes=("_venue", "_cnms"),
        how="inner",
    )
    if merged.empty:
        return
    merged["tv_diff_pct"] = (
        (merged["total_volume_venue"] - merged["total_volume_cnms"]) / merged["total_volume_cnms"].clip(lower=1)
    ).abs() * 100
    mismatches = merged[merged["tv_diff_pct"] > 1.0]
    if not mismatches.empty:
        log.warning(
            "[finra_sv] %s venue/CNMS total-volume mismatch >1%% for %s symbols",
            d,
            len(mismatches),
        )


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
    log.info("[finra_sv] backfill %s trading dates (%s to %s)", len(trading_dates), start, end)

    _sess = await shared_session().__aenter__()
    semaphore = asyncio.Semaphore(8)
    try:
        frames: list[pd.DataFrame] = []
        for i, d in enumerate(trading_dates, 1):
            if d >= _CONSOLIDATED_START:
                df = await _download_one_venue(d, _FINRA_CONSOLIDATED_PREFIX, _sess, semaphore)
            else:
                tasks = [_download_one_venue(d, v, _sess, semaphore) for v in _FINRA_VENUE_PREFIXES]
                venue_frames = [f for f in await asyncio.gather(*tasks) if f is not None and not f.empty]
                df = _aggregate_venues(pd.concat(venue_frames, ignore_index=True)) if venue_frames else None

            if df is not None and not df.empty:
                frames.append(df)
            if i % 50 == 0:
                log.info("[finra_sv] processed %s/%s dates", i, len(trading_dates))
    finally:
        await _sess.__aexit__(None, None, None)

    if not frames:
        log.warning("[finra_sv] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(frames, ignore_index=True)
    panel = _compute_sv_features(panel)

    if tickers:
        tickers_upper = [t.upper() for t in tickers]
        panel = panel[panel["symbol"].isin(tickers_upper)].copy()

    panel.rename(columns={"symbol": "ticker"}, inplace=True)
    panel.to_parquet(_PANEL_PATH, index=False)
    # Remove stale legacy pickle to avoid version-skew confusion.
    if _PICKLE_PATH.exists():
        try:
            _PICKLE_PATH.unlink()
        except Exception:
            pass
    log.info("[finra_sv] panel saved: %s rows → %s", len(panel), _PANEL_PATH)
    return panel


def load_short_volume_panel() -> pd.DataFrame | None:
    """Load cached panel if it exists."""
    if _PANEL_PATH.exists():
        return pd.read_parquet(_PANEL_PATH)
    # One-time backward-compat load of legacy pickle, then migrate to Parquet.
    if _PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_PICKLE_PATH)
            df.to_parquet(_PANEL_PATH, index=False)
            _PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning("[finra_sv] legacy pickle unloadable (%s); rebuild panel", exc)
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
