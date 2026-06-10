"""
NAAIM Exposure Index — active investment manager equity positioning (free, no key).
Published weekly by the National Association of Active Investment Managers.

Interpretation (contrarian):
  >90  = managers nearly fully invested → limited buying power, contrarian bearish (-8)
  >80  = elevated positioning → mild bearish (-4)
  <30  = managers heavily defensive → contrarian bullish (+10)
  <50  = below-average positioning → mild bullish (+5)
  else = neutral (0)

Cached 4 days (survey is weekly, released each Wednesday).
"""

import logging
import re
import ssl
import time

log = logging.getLogger("signal.trade.aaii")

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_cache: dict = {"data": None, "ts": 0.0}
CACHE_TTL = 86400 * 4  # 4 days

_URL = "https://www.naaim.org/programs/naaim-exposure-index/"
_HDRS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_aaii_sentiment__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_aaii_sentiment__mutmut)
async def get_aaii_sentiment() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_orig() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_1() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = None
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_2() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] or now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_3() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["XXdataXX"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_4() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["DATA"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_5() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now + _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_6() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["XXtsXX"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_7() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["TS"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_8() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] <= CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_9() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["XXdataXX"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_10() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["DATA"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_11() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = None
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_12() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=None)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_13() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=None) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_14() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(None, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_15() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=None, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_16() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=None) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_17() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_18() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_19() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, ) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_20() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=None)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_21() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=16)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_22() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_23() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 201:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_24() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get(None)
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_25() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("XXdataXX")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_26() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("DATA")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_27() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = None

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_28() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = None
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_29() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(None, text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_30() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", None)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_31() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_32() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", )
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_33() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"XXExposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>XX", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_34() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"exposure index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_35() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"EXPOSURE INDEX NUMBER IS\*?:</H4><DIV[^>]*>([\d.]+)</DIV>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_36() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_37() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = None
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_38() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(None, text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_39() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", None)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_40() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_41() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", )
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_42() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"XXNAAIM Exposure Index number is\*?:?\s*([\d.]+)XX", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_43() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"naaim exposure index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_44() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM EXPOSURE INDEX NUMBER IS\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_45() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_46() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get(None)
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_47() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("XXdataXX")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_48() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("DATA")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_49() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = None

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_50() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(None)

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_51() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(None))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_52() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(2))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_53() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = None
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_54() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(None) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_55() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(None, text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_56() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", None) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_57() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_58() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", ) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_59() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"XXnew Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)XX", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_60() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_61() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"NEW DATE\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_62() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 1 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_63() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 < float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_64() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(None) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_65() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) < 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_66() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 151
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_67() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = None
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_68() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[+52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_69() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-53:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_70() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) > 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_71() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 53 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_72() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_73() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(None) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_74() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_75() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(None) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_76() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = ""
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_77() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w or hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_78() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w or lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_79() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w >= lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_80() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = None

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_81() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round(None, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_82() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, None)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_83() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round(1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_84() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, )

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_85() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) / 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_86() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) * (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_87() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure + lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_88() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w + lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_89() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 101, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_90() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 2)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_91() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure > 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_92() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 91:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_93() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = None
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_94() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "XXbearishXX", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_95() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "BEARISH", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_96() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", +8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_97() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -9
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_98() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure > 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_99() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 81:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_100() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = None
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_101() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "XXbearishXX", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_102() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "BEARISH", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_103() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", +4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_104() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -5
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_105() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure < 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_106() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 31:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_107() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = None
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_108() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "XXbullishXX", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_109() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "BULLISH", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_110() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 11
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_111() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure < 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_112() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 51:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_113() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = None
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_114() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "XXbullishXX", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_115() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "BULLISH", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_116() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 6
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_117() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = None

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_118() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "XXneutralXX", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_119() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "NEUTRAL", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_120() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 1

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_121() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = None
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_122() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "XXsourceXX": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_123() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "SOURCE": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_124() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "XXNAAIMXX",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_125() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "naaim",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_126() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "XXexposureXX": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_127() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "EXPOSURE": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_128() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "XXpct_rankXX": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_129() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "PCT_RANK": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_130() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "XXhi_52wXX": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_131() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "HI_52W": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_132() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "XXlo_52wXX": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_133() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "LO_52W": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_134() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "XXsignalXX": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_135() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "SIGNAL": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_136() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "XXscoreXX": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_137() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "SCORE": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_138() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "XXbull_pctXX": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_139() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "BULL_PCT": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_140() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "XXbear_pctXX": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_141() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "BEAR_PCT": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_142() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(None, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_143() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, None),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_144() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_145() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, ),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_146() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 + exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_147() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(101 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_148() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 2),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_149() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "XXspreadXX": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_150() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "SPREAD": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_151() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(None, 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_152() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), None),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_153() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_154() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), ),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_155() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure + (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_156() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 + exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_157() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (101 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_158() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 2),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_159() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = None
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_160() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["XXdataXX"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_161() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["DATA"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_162() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = None
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_163() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["XXtsXX"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_164() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["TS"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_165() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(None)
        return _cache.get("data")


async def x_get_aaii_sentiment__mutmut_166() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get(None)


async def x_get_aaii_sentiment__mutmut_167() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("XXdataXX")


async def x_get_aaii_sentiment__mutmut_168() -> dict | None:
    """Returns NAAIM Exposure Index signal (kept as get_aaii_sentiment for drop-in compatibility)."""
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers=_HDRS, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        # Value sits in a shortcode div immediately after the h4 heading
        m = re.search(r"Exposure Index number is\*?:</h4><div[^>]*>([\d.]+)</div>", text)
        if not m:  # fallback: plain-text inline format
            m = re.search(r"NAAIM Exposure Index number is\*?:?\s*([\d.]+)", text)
        if not m:
            return _cache.get("data")
        exposure = float(m.group(1))

        # Historical series for 52-week range context (filter to 0-150 to exclude S&P price series)
        hist_vals = [
            float(v) for v in re.findall(r"new Date\(\d+,\s*\d+,\s*\d+\),\s*([\d.]+)", text) if 0 <= float(v) <= 150
        ]
        hist_52w = hist_vals[-52:] if len(hist_vals) >= 52 else hist_vals
        hi_52w = max(hist_52w) if hist_52w else None
        lo_52w = min(hist_52w) if hist_52w else None
        pct_rank = None
        if hi_52w and lo_52w and hi_52w > lo_52w:
            pct_rank = round((exposure - lo_52w) / (hi_52w - lo_52w) * 100, 1)

        if exposure >= 90:
            signal, score = "bearish", -8
        elif exposure >= 80:
            signal, score = "bearish", -4
        elif exposure <= 30:
            signal, score = "bullish", 10
        elif exposure <= 50:
            signal, score = "bullish", 5
        else:
            signal, score = "neutral", 0

        result = {
            "source": "NAAIM",
            "exposure": exposure,
            "pct_rank": pct_rank,
            "hi_52w": hi_52w,
            "lo_52w": lo_52w,
            "signal": signal,
            "score": score,
            # Alias fields signal_engine uses for AAII
            "bull_pct": exposure,
            "bear_pct": round(100 - exposure, 1),
            "spread": round(exposure - (100 - exposure), 1),
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[naaim] {e}")
        return _cache.get("DATA")

mutants_x_get_aaii_sentiment__mutmut['_mutmut_orig'] = x_get_aaii_sentiment__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_1'] = x_get_aaii_sentiment__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_2'] = x_get_aaii_sentiment__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_3'] = x_get_aaii_sentiment__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_4'] = x_get_aaii_sentiment__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_5'] = x_get_aaii_sentiment__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_6'] = x_get_aaii_sentiment__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_7'] = x_get_aaii_sentiment__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_8'] = x_get_aaii_sentiment__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_9'] = x_get_aaii_sentiment__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_10'] = x_get_aaii_sentiment__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_11'] = x_get_aaii_sentiment__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_12'] = x_get_aaii_sentiment__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_13'] = x_get_aaii_sentiment__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_14'] = x_get_aaii_sentiment__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_15'] = x_get_aaii_sentiment__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_16'] = x_get_aaii_sentiment__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_17'] = x_get_aaii_sentiment__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_18'] = x_get_aaii_sentiment__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_19'] = x_get_aaii_sentiment__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_20'] = x_get_aaii_sentiment__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_21'] = x_get_aaii_sentiment__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_22'] = x_get_aaii_sentiment__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_23'] = x_get_aaii_sentiment__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_24'] = x_get_aaii_sentiment__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_25'] = x_get_aaii_sentiment__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_26'] = x_get_aaii_sentiment__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_27'] = x_get_aaii_sentiment__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_28'] = x_get_aaii_sentiment__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_29'] = x_get_aaii_sentiment__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_30'] = x_get_aaii_sentiment__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_31'] = x_get_aaii_sentiment__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_32'] = x_get_aaii_sentiment__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_33'] = x_get_aaii_sentiment__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_34'] = x_get_aaii_sentiment__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_35'] = x_get_aaii_sentiment__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_36'] = x_get_aaii_sentiment__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_37'] = x_get_aaii_sentiment__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_38'] = x_get_aaii_sentiment__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_39'] = x_get_aaii_sentiment__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_40'] = x_get_aaii_sentiment__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_41'] = x_get_aaii_sentiment__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_42'] = x_get_aaii_sentiment__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_43'] = x_get_aaii_sentiment__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_44'] = x_get_aaii_sentiment__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_45'] = x_get_aaii_sentiment__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_46'] = x_get_aaii_sentiment__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_47'] = x_get_aaii_sentiment__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_48'] = x_get_aaii_sentiment__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_49'] = x_get_aaii_sentiment__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_50'] = x_get_aaii_sentiment__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_51'] = x_get_aaii_sentiment__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_52'] = x_get_aaii_sentiment__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_53'] = x_get_aaii_sentiment__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_54'] = x_get_aaii_sentiment__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_55'] = x_get_aaii_sentiment__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_56'] = x_get_aaii_sentiment__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_57'] = x_get_aaii_sentiment__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_58'] = x_get_aaii_sentiment__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_59'] = x_get_aaii_sentiment__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_60'] = x_get_aaii_sentiment__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_61'] = x_get_aaii_sentiment__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_62'] = x_get_aaii_sentiment__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_63'] = x_get_aaii_sentiment__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_64'] = x_get_aaii_sentiment__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_65'] = x_get_aaii_sentiment__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_66'] = x_get_aaii_sentiment__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_67'] = x_get_aaii_sentiment__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_68'] = x_get_aaii_sentiment__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_69'] = x_get_aaii_sentiment__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_70'] = x_get_aaii_sentiment__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_71'] = x_get_aaii_sentiment__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_72'] = x_get_aaii_sentiment__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_73'] = x_get_aaii_sentiment__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_74'] = x_get_aaii_sentiment__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_75'] = x_get_aaii_sentiment__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_76'] = x_get_aaii_sentiment__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_77'] = x_get_aaii_sentiment__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_78'] = x_get_aaii_sentiment__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_79'] = x_get_aaii_sentiment__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_80'] = x_get_aaii_sentiment__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_81'] = x_get_aaii_sentiment__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_82'] = x_get_aaii_sentiment__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_83'] = x_get_aaii_sentiment__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_84'] = x_get_aaii_sentiment__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_85'] = x_get_aaii_sentiment__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_86'] = x_get_aaii_sentiment__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_87'] = x_get_aaii_sentiment__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_88'] = x_get_aaii_sentiment__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_89'] = x_get_aaii_sentiment__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_90'] = x_get_aaii_sentiment__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_91'] = x_get_aaii_sentiment__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_92'] = x_get_aaii_sentiment__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_93'] = x_get_aaii_sentiment__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_94'] = x_get_aaii_sentiment__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_95'] = x_get_aaii_sentiment__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_96'] = x_get_aaii_sentiment__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_97'] = x_get_aaii_sentiment__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_98'] = x_get_aaii_sentiment__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_99'] = x_get_aaii_sentiment__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_100'] = x_get_aaii_sentiment__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_101'] = x_get_aaii_sentiment__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_102'] = x_get_aaii_sentiment__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_103'] = x_get_aaii_sentiment__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_104'] = x_get_aaii_sentiment__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_105'] = x_get_aaii_sentiment__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_106'] = x_get_aaii_sentiment__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_107'] = x_get_aaii_sentiment__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_108'] = x_get_aaii_sentiment__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_109'] = x_get_aaii_sentiment__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_110'] = x_get_aaii_sentiment__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_111'] = x_get_aaii_sentiment__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_112'] = x_get_aaii_sentiment__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_113'] = x_get_aaii_sentiment__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_114'] = x_get_aaii_sentiment__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_115'] = x_get_aaii_sentiment__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_116'] = x_get_aaii_sentiment__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_117'] = x_get_aaii_sentiment__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_118'] = x_get_aaii_sentiment__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_119'] = x_get_aaii_sentiment__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_120'] = x_get_aaii_sentiment__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_121'] = x_get_aaii_sentiment__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_122'] = x_get_aaii_sentiment__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_123'] = x_get_aaii_sentiment__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_124'] = x_get_aaii_sentiment__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_125'] = x_get_aaii_sentiment__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_126'] = x_get_aaii_sentiment__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_127'] = x_get_aaii_sentiment__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_128'] = x_get_aaii_sentiment__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_129'] = x_get_aaii_sentiment__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_130'] = x_get_aaii_sentiment__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_131'] = x_get_aaii_sentiment__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_132'] = x_get_aaii_sentiment__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_133'] = x_get_aaii_sentiment__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_134'] = x_get_aaii_sentiment__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_135'] = x_get_aaii_sentiment__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_136'] = x_get_aaii_sentiment__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_137'] = x_get_aaii_sentiment__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_138'] = x_get_aaii_sentiment__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_139'] = x_get_aaii_sentiment__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_140'] = x_get_aaii_sentiment__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_141'] = x_get_aaii_sentiment__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_142'] = x_get_aaii_sentiment__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_143'] = x_get_aaii_sentiment__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_144'] = x_get_aaii_sentiment__mutmut_144 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_145'] = x_get_aaii_sentiment__mutmut_145 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_146'] = x_get_aaii_sentiment__mutmut_146 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_147'] = x_get_aaii_sentiment__mutmut_147 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_148'] = x_get_aaii_sentiment__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_149'] = x_get_aaii_sentiment__mutmut_149 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_150'] = x_get_aaii_sentiment__mutmut_150 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_151'] = x_get_aaii_sentiment__mutmut_151 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_152'] = x_get_aaii_sentiment__mutmut_152 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_153'] = x_get_aaii_sentiment__mutmut_153 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_154'] = x_get_aaii_sentiment__mutmut_154 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_155'] = x_get_aaii_sentiment__mutmut_155 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_156'] = x_get_aaii_sentiment__mutmut_156 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_157'] = x_get_aaii_sentiment__mutmut_157 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_158'] = x_get_aaii_sentiment__mutmut_158 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_159'] = x_get_aaii_sentiment__mutmut_159 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_160'] = x_get_aaii_sentiment__mutmut_160 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_161'] = x_get_aaii_sentiment__mutmut_161 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_162'] = x_get_aaii_sentiment__mutmut_162 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_163'] = x_get_aaii_sentiment__mutmut_163 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_164'] = x_get_aaii_sentiment__mutmut_164 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_165'] = x_get_aaii_sentiment__mutmut_165 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_166'] = x_get_aaii_sentiment__mutmut_166 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_167'] = x_get_aaii_sentiment__mutmut_167 # type: ignore # mutmut generated
mutants_x_get_aaii_sentiment__mutmut['x_get_aaii_sentiment__mutmut_168'] = x_get_aaii_sentiment__mutmut_168 # type: ignore # mutmut generated
