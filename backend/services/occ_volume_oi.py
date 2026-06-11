#!/usr/bin/env python3
"""§110 — OCC daily volume and open interest by symbol.

OCC market-data reports publish daily volume + OI by symbol free:
  https://www.theocc.com/market-data/market-data-reports/volume-and-open-interest/daily-volume

No deep per-symbol history → accumulate-forward from day 1.
Provides free exchange-grade per-stock put/call ratio for the
options family (§49/§69–§72). May shrink the §98 ORATS scope to IV-only.

PIT discipline: published next-day → 1-day lag.
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

log = logging.getLogger("signal.trade.occ_volume_oi")

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_occ"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_PANEL_PATH = _CACHE_DIR / "occ_volume_oi_panel.pkl"

_cache: dict[str, tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 3600.0

# OCC daily volume report URL
_OCC_DAILY_URL = "https://www.theocc.com/webapps/daily-volume-and-open-interest"


def _parse_occ_csv(content: bytes) -> pd.DataFrame | None:
    """Parse OCC daily volume/CSV."""
    try:
        df = pd.read_csv(io.BytesIO(content), dtype=str)
        # Expected columns: Underlying, Call/Put, Volume, OI, etc.
        df = df.rename(
            columns={
                "Underlying": "ticker",
                "Call/Put": "cp",
                "Volume": "volume",
                "Open Interest": "oi",
            }
        )
        df = df.assign(
            volume=pd.to_numeric(df["volume"].astype(str).str.replace(",", ""), errors="coerce"),
            oi=pd.to_numeric(df["oi"].astype(str).str.replace(",", ""), errors="coerce"),
        )
        return df
    except Exception as exc:
        log.warning(f"[occ] parse error: {exc}")
        return None


async def download_occ_daily(
    d: date,
    session: aiohttp.ClientSession | None = None,
) -> pd.DataFrame | None:
    """Download OCC daily volume/OI report."""
    cache_key = f"occ_{d.isoformat()}"
    cached = _cache.get(cache_key)
    if cached and (time.monotonic() - cached[1] < _CACHE_TTL):
        return cached[0]

    cache_file = _CACHE_DIR / f"occ_{d.isoformat()}.csv"
    if cache_file.exists():
        try:
            df = _parse_occ_csv(cache_file.read_bytes())
            if df is not None and not df.empty:
                return df
        except Exception:
            pass

    # OCC site uses form submission; we try the direct CSV link
    url = f"{_OCC_DAILY_URL}?reportDate={d.strftime('%Y-%m-%d')}"
    try:
        _sess = session or await shared_session().__aenter__()
        async with _sess.get(url, timeout=60) as resp:
            if resp.status != 200:
                log.debug(f"[occ] {d} HTTP {resp.status}")
                return None
            content = await resp.read()
            if not content:
                return None
            cache_file.write_bytes(content)
            df = _parse_occ_csv(content)
            if df is not None and not df.empty:
                _cache[cache_key] = (df, time.monotonic())
            return df
    except Exception as exc:
        log.warning(f"[occ] {d} download error: {exc}")
        return None
    finally:
        if session is None and _sess is not None:
            await _sess.__aexit__(None, None, None)


async def build_occ_panel(
    tickers: list[str] | None = None,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    """Batch backfill OCC volume/OI panel (accumulate-forward)."""
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()

    dates = pd.bdate_range(start=start, end=end).date
    log.info(f"[occ] backfill {len(dates)} trading days ({start} to {end})")

    frames: list[pd.DataFrame] = []
    for d in dates:
        df = await download_occ_daily(d)
        if df is not None and not df.empty:
            df["date"] = d
            frames.append(df)

    if not frames:
        log.warning("[occ] no data downloaded")
        return pd.DataFrame()

    panel = pd.concat(frames, ignore_index=True)
    # Aggregate to ticker-level put/call ratios
    agg = []
    for (ticker, d), grp in panel.groupby(["ticker", "date"]):
        calls = grp[grp["cp"].str.upper() == "C"]["volume"].sum()
        puts = grp[grp["cp"].str.upper() == "P"]["volume"].sum()
        call_oi = grp[grp["cp"].str.upper() == "C"]["oi"].sum()
        put_oi = grp[grp["cp"].str.upper() == "P"]["oi"].sum()
        agg.append(
            {
                "ticker": ticker,
                "date": d,
                "call_volume": calls,
                "put_volume": puts,
                "pcr_volume": (puts / calls * 100.0) if calls > 0 else 100.0,
                "call_oi": call_oi,
                "put_oi": put_oi,
                "pcr_oi": (put_oi / call_oi * 100.0) if call_oi > 0 else 100.0,
            }
        )

    panel = pd.DataFrame(agg)
    if tickers:
        tickers_upper = [t.upper() for t in tickers]
        panel = panel[panel["ticker"].isin(tickers_upper)].copy()

    panel.to_pickle(_PANEL_PATH)
    log.info(f"[occ] panel saved: {len(panel)} rows → {_PANEL_PATH}")
    return panel


def load_occ_panel() -> pd.DataFrame | None:
    if _PANEL_PATH.exists():
        return pd.read_pickle(_PANEL_PATH)
    return None


def merge_occ_pit(
    df: pd.DataFrame,
    occ_panel: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Merge OCC volume/OI into ticker DataFrame with 1-day PIT lag."""
    if occ_panel.empty or "ticker" not in occ_panel.columns:
        df["pcr_volume"] = 100.0
        df["pcr_oi"] = 100.0
        return df

    sub = occ_panel[occ_panel["ticker"] == ticker.upper()].copy()
    if sub.empty:
        df["pcr_volume"] = 100.0
        df["pcr_oi"] = 100.0
        return df

    sub = sub.assign(date=pd.to_datetime(sub["date"]) + timedelta(days=1))
    sub = sub.sort_values("date")

    df = df.copy()
    df["_merge_date"] = pd.to_datetime(df.index)
    df = pd.merge_asof(
        df.sort_values("_merge_date"),
        sub[["date", "pcr_volume", "pcr_oi"]],
        left_on="_merge_date",
        right_on="date",
        direction="backward",
    ).copy()
    df.drop(columns=["date", "_merge_date"], inplace=True, errors="ignore")
    df = df.assign(
        pcr_volume=df["pcr_volume"].fillna(100.0),
        pcr_oi=df["pcr_oi"].fillna(100.0),
    )
    return df
