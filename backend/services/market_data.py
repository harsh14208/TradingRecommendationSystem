"""
Market data via yfinance 1.x + curl_cffi browser impersonation.

Uses a persistent Chrome-impersonating session so Yahoo Finance
doesn't block requests as bot traffic (the root cause of 429 / empty crumb).
"""
import asyncio
import random
import time as _time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import aiohttp
import pandas as pd
import pytz
import yfinance as yf
from curl_cffi import requests as curl_requests

_executor   = ThreadPoolExecutor(max_workers=4)
_yf_lock    = asyncio.Lock()    # serialise per-ticker calls that aren't batched
_YF_DELAY   = 0.8               # seconds between serialised calls

# One long-lived session that looks like Chrome — avoids Yahoo 429s
_session = curl_requests.Session(impersonate="chrome110")

# ── yfinance Global Circuit Breaker ─────────────────────────────────────────
# When yfinance returns a 429, skip all yfinance calls for 15 minutes so the
# IP rate-limit bucket resets naturally instead of compounding the ban.
_yf_backoff_until: float = 0.0   # epoch timestamp; 0 = not in backoff
_YF_BACKOFF_SECS = 900            # 15 minutes

def _yf_is_blocked() -> bool:
    return _time.time() < _yf_backoff_until

def _yf_trip_breaker():
    global _yf_backoff_until
    _yf_backoff_until = _time.time() + _YF_BACKOFF_SECS

# ── Polygon OHLCV Shared Cache ───────────────────────────────────────────────
# Keyed by (ticker, period, interval) → DataFrame + timestamp.
# 15-minute TTL: avoids redundant Polygon downloads within a scan cycle.
_ohlcv_cache: dict[tuple, dict] = {}
_OHLCV_TTL = 900   # 15 minutes

COMPANY_NAMES = {
    # ── Mega-cap core ────────────────────────────────────────────────────────
    "AAPL":  "Apple Inc.",
    "MSFT":  "Microsoft Corporation",
    "NVDA":  "NVIDIA Corporation",
    "AMZN":  "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
    "GOOG":  "Alphabet Inc.",
    "META":  "Meta Platforms, Inc.",
    "TSLA":  "Tesla, Inc.",
    "AVGO":  "Broadcom Inc.",
    "BRK-B": "Berkshire Hathaway Inc.",
    "JPM":   "JPMorgan Chase & Co.",
    "V":     "Visa Inc.",
    "LLY":   "Eli Lilly and Company",
    "WMT":   "Walmart Inc.",
    "XOM":   "Exxon Mobil Corporation",
    "UNH":   "UnitedHealth Group Inc.",
    "MA":    "Mastercard Incorporated",
    "JNJ":   "Johnson & Johnson",
    "COST":  "Costco Wholesale Corporation",
    "ORCL":  "Oracle Corporation",
    # ── AI / Semiconductor infrastructure ────────────────────────────────────
    "AMD":   "Advanced Micro Devices",
    "ASML":  "ASML Holding N.V.",
    "TSM":   "Taiwan Semiconductor Manufacturing",
    "ANET":  "Arista Networks, Inc.",
    "DELL":  "Dell Technologies Inc.",
    "APP":   "AppLovin Corporation",
    "CRWD":  "CrowdStrike Holdings, Inc.",
    "ZS":    "Zscaler, Inc.",
    "WDAY":  "Workday, Inc.",
    "TTD":   "The Trade Desk, Inc.",
    "AXON":  "Axon Enterprise, Inc.",
    # ── Cloud / SaaS ─────────────────────────────────────────────────────────
    "NFLX":  "Netflix, Inc.",
    "PLTR":  "Palantir Technologies",
    "SMCI":  "Super Micro Computer",
    "TQQQ":  "ProShares UltraPro QQQ",
    "CRM":   "Salesforce, Inc.",
    "SNOW":  "Snowflake Inc.",
    "DDOG":  "Datadog, Inc.",
    "MDB":   "MongoDB, Inc.",
    "NET":   "Cloudflare, Inc.",
    "PANW":  "Palo Alto Networks, Inc.",
    # ── Fintech / Crypto ─────────────────────────────────────────────────────
    "COIN":  "Coinbase Global, Inc.",
    "MSTR":  "MicroStrategy Incorporated",
    "PYPL":  "PayPal Holdings, Inc.",
    # ── Consumer / Travel ────────────────────────────────────────────────────
    "RCL":   "Royal Caribbean Cruises Ltd.",
    "LVS":   "Las Vegas Sands Corp.",
    "SPOT":  "Spotify Technology S.A.",
    # ── Index / Broad-market ETFs ─────────────────────────────────────────────
    "SPY":   "SPDR S&P 500 ETF Trust",
    "QQQ":   "Invesco QQQ Trust",
    "IWM":   "iShares Russell 2000 ETF",
    "TQQQ":  "ProShares UltraPro QQQ",
    # ── Sector ETFs ───────────────────────────────────────────────────────────
    "XLK":   "Technology Select Sector SPDR",
    "XLF":   "Financial Select Sector SPDR",
    "XLE":   "Energy Select Sector SPDR",
    "XLP":   "Consumer Staples Select Sector SPDR",
    "XLB":   "Materials Select Sector SPDR",
    "XLU":   "Utilities Select Sector SPDR",
    "XLY":   "Consumer Discretionary Select Sector SPDR",
    "XLC":   "Communication Services Select Sector SPDR",
    "XLI":   "Industrial Select Sector SPDR",
    "XLV":   "Health Care Select Sector SPDR",
    "XLRE":  "Real Estate Select Sector SPDR",
    # ── Bond ETFs ────────────────────────────────────────────────────────────
    "TLT":   "iShares 20+ Year Treasury Bond ETF",
    "HYG":   "iShares iBoxx High Yield Corp Bond ETF",
    # ── Commodities / Metals ─────────────────────────────────────────────────
    "GLD":   "SPDR Gold Shares",
    "SLV":   "iShares Silver Trust",
    "GDX":   "VanEck Gold Miners ETF",
    "GDXJ":  "VanEck Junior Gold Miners ETF",
    "COPX":  "Global X Copper Miners ETF",
}


def _retry(fn, *args, retries: int = 4, base_delay: float = 2.0, **kwargs):
    """Exponential back-off with ±30% jitter. Detects 429, trips the circuit breaker."""
    if _yf_is_blocked():
        raise RuntimeError("yfinance circuit breaker active — skipping to protect IP")
    last_err = None
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            is_429  = "429" in err_str or "too many" in err_str or "rate limit" in err_str
            if is_429:
                _yf_trip_breaker()  # back off for 15 min — don't keep hammering
                raise RuntimeError(f"yfinance 429 — circuit breaker tripped for {_YF_BACKOFF_SECS}s") from e
            if attempt < retries - 1:
                delay  = base_delay * (2 ** attempt)
                jitter = delay * random.uniform(-0.3, 0.3)
                _time.sleep(max(0.5, delay + jitter))
    raise last_err


# ── Batch helpers (one HTTP round-trip for many tickers) ────────────────────

def _fetch_histories_batch(
    tickers: list[str], period: str, interval: str
) -> dict[str, pd.DataFrame]:
    try:
        raw = _retry(
            yf.download,
            tickers, period=period, interval=interval,
            auto_adjust=True, progress=False, threads=False,
            session=_session,
        )
        if raw is None or raw.empty:
            return {}

        out: dict[str, pd.DataFrame] = {}
        if len(tickers) == 1:
            t = tickers[0]
            if not raw.empty:
                out[t] = raw
        else:
            for t in tickers:
                try:
                    # yfinance 1.x MultiIndex: (metric, ticker)
                    df = raw.xs(t, level=1, axis=1).dropna(how="all")
                    if not df.empty and len(df) >= 2:
                        out[t] = df
                except (KeyError, TypeError):
                    pass
        return out
    except Exception as e:
        print(f"[market_data] batch history error: {e}")
        return {}


def _fetch_quotes_batch(tickers: list[str]) -> list[dict]:
    try:
        raw = _retry(
            yf.download,
            tickers, period="2d", interval="1d",  # 2d is enough for current + prev close
            auto_adjust=True, progress=False, threads=False,
            session=_session,
        )
        if raw is None or raw.empty:
            return []

        out = []
        if len(tickers) == 1:
            t     = tickers[0]
            close = raw["Close"]
            if len(close) >= 2:
                price = float(close.iloc[-1])
                prev  = float(close.iloc[-2])
                out.append({"t": t, "p": round(price, 2),
                            "c": round((price - prev) / prev * 100, 2)})
        else:
            close = raw["Close"]
            for t in tickers:
                try:
                    s = close[t].dropna()
                    if len(s) < 2:
                        continue
                    price = float(s.iloc[-1])
                    prev  = float(s.iloc[-2])
                    out.append({"t": t, "p": round(price, 2),
                                "c": round((price - prev) / prev * 100, 2)})
                except (KeyError, TypeError):
                    pass
        return out
    except Exception as e:
        print(f"[market_data] batch quotes error: {e}")
        return []


# ── Per-ticker helpers ───────────────────────────────────────────────────────

def _fetch_history(ticker: str, period: str, interval: str,
                   prepost: bool = False) -> Optional[pd.DataFrame]:
    try:
        df = _retry(
            yf.Ticker(ticker, session=_session).history,
            period=period, interval=interval, auto_adjust=True,
            prepost=prepost,
        )
        return df if (df is not None and not df.empty) else None
    except Exception:
        return None


def _get_premarket_price(ticker: str) -> Optional[float]:
    """Return the most recent pre-market or after-hours price for a ticker."""
    try:
        df = _fetch_history(ticker, period="1d", interval="1m", prepost=True)
        if df is not None and not df.empty:
            return round(float(df["Close"].iloc[-1]), 2)
    except Exception:
        pass
    return None


def _fetch_info(ticker: str) -> dict:
    try:
        info   = _retry(lambda: yf.Ticker(ticker, session=_session).info)
        sfloat = info.get("shortPercentOfFloat")
        return {
            "company":         info.get("longName", COMPANY_NAMES.get(ticker, ticker)),
            "pe":              info.get("trailingPE"),
            "market_cap":      info.get("marketCap"),
            "volume":          info.get("volume"),
            "avg_volume":      info.get("averageVolume"),
            "short_float_pct": round(float(sfloat) * 100, 2) if sfloat else None,
            "short_ratio":     info.get("shortRatio"),
            "beta":            info.get("beta"),
            # Analyst price targets & consensus (free via yfinance)
            "target_mean":     info.get("targetMeanPrice"),
            "target_high":     info.get("targetHighPrice"),
            "target_low":      info.get("targetLowPrice"),
            "analyst_count":   info.get("numberOfAnalystOpinions"),
            "rec_mean":        info.get("recommendationMean"),   # 1=Strong Buy ... 5=Strong Sell
            "rec_key":         info.get("recommendationKey"),    # "buy", "hold", "sell", etc.
        }
    except Exception:
        return {"company": COMPANY_NAMES.get(ticker, ticker)}


async def _rate_limited(fn, *args):
    async with _yf_lock:
        result = await asyncio.get_running_loop().run_in_executor(_executor, fn, *args)
        await asyncio.sleep(_YF_DELAY)
        return result


# ── Public async API ─────────────────────────────────────────────────────────

async def get_histories_batch(
    tickers: list[str], period: str = "1y", interval: str = "1d"
) -> dict[str, pd.DataFrame]:
    return await asyncio.get_running_loop().run_in_executor(
        _executor, _fetch_histories_batch, tickers, period, interval
    )


async def get_quotes_batch(tickers: list[str]) -> list[dict]:
    """
    Fetch current quotes via yfinance 2d batch (optimised from 5d → 2d).
    Polygon grouped-daily is rate-limited on the free tier for 150+ tickers,
    so yfinance batch remains the fastest path for bulk quote fetching.
    """
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_quotes_batch, tickers)


async def get_infos_sequential(tickers: list[str]) -> dict[str, dict]:
    """Fetch .info for each ticker one at a time with rate-limiting."""
    result: dict[str, dict] = {}
    for t in tickers:
        result[t] = await _rate_limited(_fetch_info, t)
    return result


# Single-ticker wrappers (used by macro.py, routers, etc.)
async def get_history(
    ticker: str, period: str = "3mo", interval: str = "1d"
) -> Optional[pd.DataFrame]:
    # Check shared OHLCV cache first — avoids redundant Polygon calls within a scan cycle
    _cache_key = (ticker.upper(), period, interval)
    _now = _time.time()
    if _cache_key in _ohlcv_cache and _now - _ohlcv_cache[_cache_key]["ts"] < _OHLCV_TTL:
        return _ohlcv_cache[_cache_key]["df"]

    # Prefer Polygon.io when key is configured — more reliable than yfinance
    try:
        from config import get_settings
        s = get_settings()
        if s.polygon_api_key or s.massive_api_key:
            from services.polygon_client import get_polygon_history
            df = await get_polygon_history(ticker, period=period, interval=interval)
            if df is not None and not df.empty and len(df) >= 2:
                _ohlcv_cache[_cache_key] = {"df": df, "ts": _now}
                return df
    except Exception:
        pass

    if _yf_is_blocked():
        return None
    df = await _rate_limited(_fetch_history, ticker, period, interval)
    if df is not None and not df.empty:
        _ohlcv_cache[_cache_key] = {"df": df, "ts": _now}
    return df


def _fetch_extended_hours(ticker: str) -> Optional[dict]:
    """
    Return extended-hours (pre-market / after-hours) stats vs the previous
    regular-session close.  Uses 1-minute bars with prepost=True so the most
    recent tick reflects the live extended-hours price.
    """
    try:
        df = _fetch_history(ticker, period="2d", interval="1m", prepost=True)
        if df is None or len(df) < 2:
            return None

        et = pytz.timezone("America/New_York")

        # Attach ET timezone to the index for hour-filtering
        if df.index.tzinfo is None:
            idx = df.index.tz_localize("UTC").tz_convert(et)
        else:
            idx = df.index.tz_convert(et)

        # Previous regular-session close: last bar between 9:30–16:00 ET
        reg_mask = idx.map(lambda t: 9 * 60 + 30 <= t.hour * 60 + t.minute < 16 * 60)
        reg_bars = df[reg_mask]
        if reg_bars.empty:
            return None
        prev_close = float(reg_bars["Close"].iloc[-1])

        # Latest extended-hours bar: before 9:30 or after 16:00
        ext_mask = idx.map(lambda t: t.hour * 60 + t.minute < 9 * 60 + 30
                                     or t.hour * 60 + t.minute >= 16 * 60)
        ext_bars = df[ext_mask]
        if ext_bars.empty:
            return None

        ext_price  = float(ext_bars["Close"].iloc[-1])
        gap_pct    = round((ext_price - prev_close) / prev_close * 100, 3)
        ext_volume = int(ext_bars["Volume"].sum())

        # Approximate avg extended-hours volume from yesterday's extended bars
        yesterday_ext = ext_bars.iloc[:-len(ext_bars[idx[ext_mask] == idx[ext_mask].max().normalize()])]
        avg_ext_vol   = int(yesterday_ext["Volume"].sum()) if not yesterday_ext.empty else ext_volume

        vol_ratio  = round(ext_volume / avg_ext_vol, 2) if avg_ext_vol > 0 else 1.0
        direction  = "up" if gap_pct > 0.1 else "down" if gap_pct < -0.1 else "flat"

        return {
            "price":      ext_price,
            "prev_close": prev_close,
            "gap_pct":    gap_pct,
            "vol_ratio":  vol_ratio,
            "direction":  direction,
            "ext_volume": ext_volume,
        }
    except Exception:
        return None


async def get_extended_hours_data(ticker: str) -> Optional[dict]:
    return await _rate_limited(_fetch_extended_hours, ticker)


async def get_quote(ticker: str) -> Optional[dict]:
    quotes = await get_quotes_batch([ticker])
    return quotes[0] if quotes else None


async def get_quotes(tickers: list[str]) -> list[dict]:
    return await get_quotes_batch(tickers)


async def get_info(ticker: str) -> dict:
    return await _rate_limited(_fetch_info, ticker)
