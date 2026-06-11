#!/usr/bin/env python3
"""§105 — SEC fails-to-deliver (FTD) direct downloader.

SEC publishes half-month FTD CSV files free at:
  https://www.sec.gov/data/foiadocsfailsdatahtm

History: 2004+ (CSV format). Each file covers ~half a month.
Published ~15–30 days after the settlement date.

PIT discipline: as-of-join on **publication date**, not trade date.
Conservative lag: 30 days.
"""

from __future__ import annotations

import io
import time
import logging
import os
from datetime import date, timedelta
from pathlib import Path

import aiohttp
import pandas as pd

from services.http_client import shared_session

log = logging.getLogger("signal.trade.sec_ftd")

# SEC FTD archive URL template
# Files are named: cnsfails{YYYYMM}.zip  (full month, contains two half-month CSVs)
_SEC_FTD_URL = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails{yyyymm}{half}.zip"

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_sec_ftd"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "sec_ftd_panel.pkl"

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0

# SEC requests a custom user-agent
_SEC_USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "Signal.Trade Research Bot (signal@example.com)",
)


def _parse_ftd_csv(content: bytes) -> pd.DataFrame | None:
    """Parse an SEC FTD file (pipe-delimited, with header)."""
    try:
        df = pd.read_csv(
            io.BytesIO(content),
            sep="|",
            dtype={
                "SETTLEMENT DATE": str,
                "CUSIP": str,
                "SYMBOL": str,
                "QUANTITY (FAILS)": str,
                "DESCRIPTION": str,
                "PRICE": str,
            },
        )
        df = df.rename(
            columns={
                "SETTLEMENT DATE": "settlement_date",
                "CUSIP": "cusip",
                "SYMBOL": "symbol",
                "QUANTITY (FAILS)": "ftd_shares",
                "DESCRIPTION": "description",
                "PRICE": "price",
            }
        )
        df = df.assign(
            settlement_date=pd.to_datetime(df["settlement_date"], format="%Y%m%d", errors="coerce").dt.date,
            ftd_shares=df["ftd_shares"].astype(str).str.replace(",", "").astype(int, errors="ignore"),
        )
        df = df.dropna(subset=["settlement_date"])
        df = df[df["symbol"].notna() & (df["symbol"] != "")]
        return df
    except Exception as exc:
        log.warning(f"[sec_ftd] parse error: {exc}")
        return None


async def download_sec_ftd(
    year: int,
    month: int,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download SEC FTD ZIPs for a given year+month (both halves). Never raises."""
    cache_key = f"ftd_{year:04d}{month:02d}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    yyyymm = f"{year:04d}{month:02d}"
    headers = {"User-Agent": _SEC_USER_AGENT}
    frames: list[pd.DataFrame] = []
    _sess = session
    try:
        _sess = _sess or await shared_session().__aenter__()
        for half in ("a", "b"):
            zip_path = _CACHE_DIR / f"cnsfails{yyyymm}{half}.zip"
            if zip_path.exists():
                try:
                    df = _extract_ftd_from_zip(zip_path)
                    if df is not None:
                        frames.append(df)
                    continue
                except Exception:
                    pass
            url = _SEC_FTD_URL.format(yyyymm=yyyymm, half=half)
            try:
                async with _sess.get(url, headers=headers, timeout=60) as resp:
                    if resp.status != 200:
                        log.debug(f"[sec_ftd] {yyyymm}{half} HTTP {resp.status}")
                        continue
                    content = await resp.read()
                    if not content:
                        continue
                    zip_path.write_bytes(content)
                    df = _extract_ftd_from_zip(zip_path)
                    if df is not None:
                        frames.append(df)
            except Exception as exc:
                log.debug(f"[sec_ftd] {yyyymm}{half} download error: {exc}")
    except Exception as exc:
        log.warning(f"[sec_ftd] {yyyymm} download error: {exc}")
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)

    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    _cache[cache_key] = (df, time.monotonic())
    return df


def _extract_ftd_from_zip(zip_path: Path) -> pd.DataFrame | None:
    """Extract and parse all CSV/TXT files inside an SEC FTD ZIP."""
    frames: list[pd.DataFrame] = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                # SEC FTD files often have no extension (e.g. "cnsfails202401a")
                base = name.lower().split("/")[-1]
                if base.endswith(".zip") or base.startswith("__"):
                    continue
                content = zf.read(name)
                df = _parse_ftd_csv(content)
                if df is not None and not df.empty:
                    frames.append(df)
    except Exception as exc:
        log.warning(f"[sec_ftd] zip extract error: {exc}")
        return None
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


import zipfile


def _compute_ftd_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute FTD ratio and 63d percentile per ticker."""
    df = df.copy()
    df = df.sort_values(["symbol", "settlement_date"]).copy()
    # 63-day rolling percentile within ticker
    df = df.assign(
        ftd_63d_pctile=df.groupby("symbol")["ftd_shares"]
        .rolling(63, min_periods=10)
        .apply(lambda x: x.rank(pct=True).iloc[-1] * 100, raw=False)
        .reset_index(level=0, drop=True)
    )
    return df


async def build_ftd_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Batch backfill SEC FTD panel. Idempotent (skips existing files).

    If start is None, defaults to 2004-01-01.
    If end is None, defaults to today.
    """
    if start is None:
        start = date(2004, 1, 1)
    if end is None:
        end = date.today()

    # Generate all year-month pairs in range
    months = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        months.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1

    log.info(f"[sec_ftd] backfill {len(months)} months ({start} to {end})")

    frames: list[pd.DataFrame] = []
    for y, m in months:
        df = await download_sec_ftd(y, m)
        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        log.warning("[sec_ftd] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(frames, ignore_index=True)
    panel = _compute_ftd_features(panel)

    if tickers:
        tickers_upper = [t.upper() for t in tickers]
        panel = panel[panel["symbol"].isin(tickers_upper)].copy()

    panel = panel.rename(columns={"symbol": "ticker"})
    # Apply conservative 30-day publication lag for PIT
    panel = panel.assign(effective_date=panel["settlement_date"] + timedelta(days=30))

    panel.to_pickle(_PANEL_PATH)
    log.info(f"[sec_ftd] panel saved: {len(panel)} rows → {_PANEL_PATH}")
    return panel


def load_ftd_panel() -> pd.DataFrame | None:
    """Load cached panel if it exists."""
    if _PANEL_PATH.exists():
        return pd.read_pickle(_PANEL_PATH)
    return None


def merge_ftd_pit(
    df: pd.DataFrame,
    ftd_panel: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Merge SEC FTD into a ticker DataFrame with PIT discipline.

    SEC FTD is published ~15–30d after settlement. We merge on effective_date
    (= settlement_date + 30d) with backward-asof to enforce the lag.
    """
    if ftd_panel.empty or "ticker" not in ftd_panel.columns:
        df["ftd_shares"] = 0
        df["ftd_63d_pctile"] = 50.0
        return df

    ftd = ftd_panel[ftd_panel["ticker"] == ticker.upper()][["effective_date", "ftd_shares", "ftd_63d_pctile"]].copy()
    if ftd.empty:
        df["ftd_shares"] = 0
        df["ftd_63d_pctile"] = 50.0
        return df

    ftd = ftd.assign(effective_date=pd.to_datetime(ftd["effective_date"]))
    ftd = ftd.sort_values("effective_date")

    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)
    df = pd.merge_asof(
        df.sort_values("_merge_date"),
        ftd,
        left_on="_merge_date",
        right_on="effective_date",
        direction="backward",
    ).copy()
    df.drop(columns=["effective_date", "_merge_date"], inplace=True, errors="ignore")
    df = df.assign(
        ftd_shares=df["ftd_shares"].fillna(0).astype(int),
        ftd_63d_pctile=df["ftd_63d_pctile"].fillna(50.0),
    )
    return df
