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
