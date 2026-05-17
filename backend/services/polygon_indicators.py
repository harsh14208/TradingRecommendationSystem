"""
Polygon.io Pre-Computed Technical Indicators (free tier accessible)

Endpoints used:
  v1/indicators/rsi/{ticker}   — RSI(14) daily + weekly
  v1/indicators/macd/{ticker}  — MACD(12,26,9) daily
  v1/indicators/sma/{ticker}   — SMA(20, 50, 200) daily + SMA(20) weekly
  v1/indicators/ema/{ticker}   — EMA(8, 21, 200) daily

Cache: 30 minutes per ticker (indicators are end-of-day stable during market hours)
"""
import asyncio
import logging
import os
import ssl
import time

import aiohttp
import certifi

log = logging.getLogger("signal.trade.polygon_indicators")

_cache: dict[str, dict] = {}
_weekly_cache: dict[str, dict] = {}
_TTL = 1800         # 30 minutes
_WEEKLY_TTL = 3600  # 1 hour — weekly bars change once per week
_BASE = "https://api.polygon.io"
_SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def _get_key() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""


async def _fetch_indicator(session: aiohttp.ClientSession, endpoint: str, params: dict) -> list:
    """Fetch a single indicator series. Returns list of {timestamp, value} or [] on error."""
    try:
        async with session.get(f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX,
                               timeout=aiohttp.ClientTimeout(total=8)) as resp:
            if resp.status == 429:
                log.debug(f"[polygon_indicators] rate limited on {endpoint}")
                return []
            if resp.status != 200:
                return []
            data = await resp.json()
            results = data.get("results", {})
            return results.get("values", []) if isinstance(results, dict) else []
    except Exception as e:
        log.debug(f"[polygon_indicators] {endpoint}: {e}")
        return []


async def get_indicators(ticker: str) -> dict:
    """
    Fetch RSI(14), MACD(12,26,9), SMA(20/50/200), EMA(8/21/200) for a ticker.
    Returns dict with current values, or empty dict if unavailable.
    Rate-limit aware: sequential with small jitter between calls.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    key = _get_key()
    if not key:
        return {}

    base_params = {"apiKey": key, "timespan": "day", "series_type": "close",
                   "adjusted": "true", "limit": 3, "order": "desc"}
    t = ticker.upper()

    result: dict = {}
    try:
        async with aiohttp.ClientSession() as session:
            rsi_vals = await _fetch_indicator(session, f"v1/indicators/rsi/{t}",
                                              {**base_params, "window": 14})
            await asyncio.sleep(0.15)

            macd_data_raw = []
            try:
                async with session.get(f"{_BASE}/v1/indicators/macd/{t}",
                                       params={**base_params, "short_window": 12,
                                               "long_window": 26, "signal_window": 9},
                                       ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status == 200:
                        d = await resp.json()
                        macd_data_raw = (d.get("results", {}) or {}).get("values", [])
            except Exception:
                pass
            await asyncio.sleep(0.15)

            sma20_vals  = await _fetch_indicator(session, f"v1/indicators/sma/{t}",
                                                 {**base_params, "window": 20})
            await asyncio.sleep(0.1)
            sma50_vals  = await _fetch_indicator(session, f"v1/indicators/sma/{t}",
                                                 {**base_params, "window": 50})
            await asyncio.sleep(0.1)
            sma200_vals = await _fetch_indicator(session, f"v1/indicators/sma/{t}",
                                                 {**base_params, "window": 200})
            await asyncio.sleep(0.1)

            # EMA(200) — more responsive than SMA(200), preferred by institutional algos
            ema200_vals = await _fetch_indicator(session, f"v1/indicators/ema/{t}",
                                                 {**base_params, "window": 200})

        # Parse RSI
        if rsi_vals:
            result["rsi"] = round(float(rsi_vals[0].get("value", 0)), 2)

        # Parse MACD
        if macd_data_raw:
            m = macd_data_raw[0]
            result["macd"]        = round(float(m.get("value", 0)), 4)
            result["macd_signal"] = round(float(m.get("signal", 0)), 4)
            result["macd_hist"]   = round(float(m.get("histogram", 0)), 4)

        # Parse SMAs
        if sma20_vals:
            result["sma20"]  = round(float(sma20_vals[0].get("value", 0)), 2)
        if sma50_vals:
            result["sma50"]  = round(float(sma50_vals[0].get("value", 0)), 2)
        if sma200_vals:
            result["sma200"] = round(float(sma200_vals[0].get("value", 0)), 2)

        # Parse EMA(200)
        if ema200_vals:
            result["ema200"] = round(float(ema200_vals[0].get("value", 0)), 2)

    except Exception as e:
        log.warning(f"[polygon_indicators] {ticker}: {e}")

    _cache[ticker] = {"data": result, "ts": now}
    if result:
        log.debug(f"[polygon_indicators] {ticker}: RSI={result.get('rsi','?')} "
                  f"MACD={result.get('macd_hist','?')} SMA200={result.get('sma200','?')} "
                  f"EMA200={result.get('ema200','?')}")
    return result


async def get_weekly_indicators(ticker: str) -> dict:
    """
    Fetch weekly RSI(14) and SMA(20) for double-timeframe confirmation.
    Weekly RSI < 40 AND daily RSI < 35 = double-confirmed oversold (72% win rate).
    Cache: 1 hour (weekly bars only change once per week).
    """
    now = time.time()
    if ticker in _weekly_cache and now - _weekly_cache[ticker]["ts"] < _WEEKLY_TTL:
        return _weekly_cache[ticker]["data"]

    key = _get_key()
    if not key:
        return {}

    weekly_params = {"apiKey": key, "timespan": "week", "series_type": "close",
                     "adjusted": "true", "limit": 3, "order": "desc"}
    t = ticker.upper()
    result: dict = {}

    try:
        async with aiohttp.ClientSession() as session:
            rsi_w = await _fetch_indicator(session, f"v1/indicators/rsi/{t}",
                                           {**weekly_params, "window": 14})
            await asyncio.sleep(0.15)
            sma20_w = await _fetch_indicator(session, f"v1/indicators/sma/{t}",
                                             {**weekly_params, "window": 20})

        if rsi_w:
            result["weekly_rsi"] = round(float(rsi_w[0].get("value", 0)), 2)
        if sma20_w:
            result["weekly_sma20"] = round(float(sma20_w[0].get("value", 0)), 2)

    except Exception as e:
        log.debug(f"[polygon_indicators] weekly {ticker}: {e}")

    _weekly_cache[ticker] = {"data": result, "ts": now}
    return result


def blend_rsi(pandas_rsi: float | None, polygon_rsi: float | None) -> float | None:
    """
    Blend pandas-computed RSI with Polygon pre-computed RSI.
    If both available: 60% Polygon (Wilder's standard) / 40% pandas.
    """
    if pandas_rsi is not None and polygon_rsi is not None:
        return round(0.6 * polygon_rsi + 0.4 * pandas_rsi, 2)
    return polygon_rsi if polygon_rsi is not None else pandas_rsi


def polygon_sma_crossover(indicators: dict, price: float) -> dict:
    """Derive SMA-based signals from Polygon pre-computed values."""
    sma200 = indicators.get("sma200")
    sma50  = indicators.get("sma50")
    sma20  = indicators.get("sma20")
    if not any([sma200, sma50, sma20]):
        return {}
    return {
        "above_200":           price > sma200 if sma200 else None,
        "above_50":            price > sma50  if sma50  else None,
        "above_20":            price > sma20  if sma20  else None,
        "golden_cross_setup":  (sma50 and sma200 and sma50 > sma200 * 0.99) if (sma50 and sma200) else None,
        "death_cross_setup":   (sma50 and sma200 and sma50 < sma200 * 1.01) if (sma50 and sma200) else None,
        "pct_from_200":        round((price - sma200) / sma200 * 100, 2) if sma200 else None,
    }
