#!/usr/bin/env python3
"""§108 — FINRA ATS dark-pool weekly per-ticker volumes.

FINRA publishes weekly per-security ATS volumes free since Rule 4552
(Jan 2014):
  https://www.finra.org/filing-reporting/otc-transparency
  https://www.finra.org/sites/default/files/OTC-Transparency-Data-File-Download-API-v04.pdf

2-week publication lag (Tier 1) → slow regime/quality feature, not an entry
trigger. Dark-pool share trend as institutional-participation context for
L8-style quality sizing. 12 years backtestable.

PIT discipline: 14-day publication lag.
"""

from __future__ import annotations

import io
import logging
import time
from datetime import date, timedelta
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.finra_ats_dark_pool")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_finra_ats"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "finra_ats_panel.parquet"
_PICKLE_PATH = _CACHE_DIR / "finra_ats_panel.pkl"  # legacy

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 86400.0

# Track whether we've already logged the HTML-block message so we don't spam
# one warning per week during a bulk backfill.
_HTML_WARNED = False

# FINRA OTC Transparency file-download API
_FINRA_OTC_URL = "https://otctransparency.finra.org/api/v1/download"


def _parse_ats_csv(content: bytes) -> pd.DataFrame | None:
    """Parse FINRA ATS weekly CSV."""
    if content.lstrip()[:9].lower() == b"<!doctype":
        return None
    try:
        df = pd.read_csv(io.BytesIO(content), dtype=str)
        # Expected columns vary by year; common ones:
        # IssueSymbolIdentifier, TotalWeeklyShareQuantity, TotalWeeklyTradeCount,
        # ATSShareQuantity, ATSTradeCount, MediaShareQuantity, etc.
        df = df.rename(
            columns={
                "IssueSymbolIdentifier": "ticker",
                "TotalWeeklyShareQuantity": "total_volume",
                "ATSShareQuantity": "ats_volume",
                "MediaShareQuantity": "media_volume",
            }
        )
        if "week_start_date" in df.columns:
            ws = pd.to_datetime(df["week_start_date"]).dt.date
        elif "Date" in df.columns:
            ws = pd.to_datetime(df["Date"]).dt.date
        else:
            ws = date.today()
        df = df.assign(
            week_start_date=ws,
            ats_volume=pd.to_numeric(df["ats_volume"].astype(str).str.replace(",", ""), errors="coerce"),
            total_volume=pd.to_numeric(df["total_volume"].astype(str).str.replace(",", ""), errors="coerce"),
        )
        df = df.assign(ats_ratio=(df["ats_volume"] / df["total_volume"] * 100.0).where(df["total_volume"] > 0))
        return df
    except Exception as exc:
        log.warning(f"[finra_ats] parse error: {exc}")
        return None


async def download_finra_ats_week(
    week_start: date,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download FINRA ATS data for a given week."""
    cache_key = f"ats_{week_start.isoformat()}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    cache_file = _CACHE_DIR / f"ats_{week_start.isoformat()}.csv"
    if cache_file.exists():
        try:
            df = _parse_ats_csv(cache_file.read_bytes())
            if df is not None and not df.empty:
                return df
        except Exception:
            pass

    # FINRA API requires form-data POST
    try:
        _sess = session or await shared_session().__aenter__()
        payload = {
            "date": week_start.strftime("%Y-%m-%d"),
            "type": "ATS_WEEKLY",
        }
        async with _sess.post(_FINRA_OTC_URL, data=payload, timeout=60) as resp:
            if resp.status != 200:
                log.debug(f"[finra_ats] {week_start} HTTP {resp.status}")
                return None
            content = await resp.read()
            if not content:
                return None
            # The legacy OTC Transparency SPA now returns HTML instead of CSV.
            # Historical backfill via this endpoint is blocked; the newer
            # api.finra.org endpoint only exposes a limited sample and lacks
            # the per-ticker total-volume denominator needed for ats_ratio.
            global _HTML_WARNED
            if content.lstrip()[:9].lower() == b"<!doctype":
                if not _HTML_WARNED:
                    log.warning(
                        "[finra_ats] endpoint returned HTML (CSV unavailable). "
                        "Historical backfill is currently blocked; live-forward accumulation only."
                    )
                    _HTML_WARNED = True
                return None
            cache_file.write_bytes(content)
            df = _parse_ats_csv(content)
            if df is not None and not df.empty:
                _cache[cache_key] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[finra_ats] {week_start} download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


async def build_ats_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Batch backfill FINRA ATS panel."""
    if start is None:
        start = date(2014, 1, 6)  # First Monday after Rule 4552
    if end is None:
        end = date.today()

    # Generate Monday starts
    mondays = pd.date_range(start=start, end=end, freq="W-MON").date
    log.info(f"[finra_ats] backfill {len(mondays)} weeks ({start} to {end})")

    frames: list[pd.DataFrame] = []
    for mon in mondays:
        df = await download_finra_ats_week(mon)
        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        log.warning("[finra_ats] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(frames, ignore_index=True)
    if tickers:
        tickers_upper = [t.upper() for t in tickers]
        panel = panel[panel["ticker"].isin(tickers_upper)].copy()

    panel.to_parquet(_PANEL_PATH, index=False)
    if _PICKLE_PATH.exists():
        try:
            _PICKLE_PATH.unlink()
        except Exception:
            pass
    log.info(f"[finra_ats] panel saved: {len(panel)} rows → {_PANEL_PATH}")
    return panel


def load_ats_panel() -> pd.DataFrame | None:
    if _PANEL_PATH.exists():
        return pd.read_parquet(_PANEL_PATH)
    if _PICKLE_PATH.exists():
        try:
            df = pd.read_pickle(_PICKLE_PATH)
            df.to_parquet(_PANEL_PATH, index=False)
            _PICKLE_PATH.unlink()
            return df
        except Exception as exc:
            log.warning(f"[finra_ats] legacy pickle unloadable ({exc}); rebuild panel")
    return None


def merge_ats_pit(
    df: pd.DataFrame,
    ats_panel: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Merge FINRA ATS into ticker DataFrame with 14-day PIT lag."""
    if ats_panel.empty or "ticker" not in ats_panel.columns:
        df["ats_ratio"] = 50.0
        return df

    sub = ats_panel[ats_panel["ticker"] == ticker.upper()].copy()
    if sub.empty:
        df["ats_ratio"] = 50.0
        return df

    sub = sub.assign(week_start_date=pd.to_datetime(sub["week_start_date"]) + timedelta(days=14))
    sub = sub.sort_values("week_start_date")

    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)
    df = pd.merge_asof(
        df.sort_values("_merge_date"),
        sub[["week_start_date", "ats_ratio"]],
        left_on="_merge_date",
        right_on="week_start_date",
        direction="backward",
    ).copy()
    df.drop(columns=["week_start_date", "_merge_date"], inplace=True, errors="ignore")
    df = df.assign(ats_ratio=df["ats_ratio"].fillna(50.0))
    return df
