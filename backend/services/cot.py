"""
CFTC Commitment of Traders (COT) — S&P 500 E-mini futures.
Parsed directly from the CFTC Financial Futures HTML report (free, no key).
Published every Friday for the prior Tuesday.
Cached 4 days.

Column order in the CFTC Financial Futures legacy report (positions line):
  0  Dealer Long
  1  Dealer Short
  2  Dealer Spreading
  3  Asset Manager Long
  4  Asset Manager Short
  5  Asset Manager Spreading
  6  Leveraged Funds Long
  7  Leveraged Funds Short
  8  Leveraged Funds Spreading
  9  Other Reportables Long
  10 Other Reportables Short
"""

import re
import ssl
import time

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_cache: dict = {"data": None, "ts": 0.0}
CACHE_TTL = 86400 * 4  # 4 days

_URL = "https://www.cftc.gov/dea/futures/financial_lf.htm"


async def get_cot_signal() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = await r.text()

        lines = text.split("\n")
        pos_line = None
        as_of = ""

        for i, line in enumerate(lines):
            # Match E-MINI S&P 500 header (exclude sector ETF variants)
            if "E-MINI S&P 500 -" in line.upper() and "SELECT" not in line.upper():
                # "Positions" is 2 lines down, numbers are 3 lines down
                for j in range(i, min(i + 6, len(lines))):
                    if "Positions" in lines[j]:
                        nums_line = lines[j + 1] if j + 1 < len(lines) else ""
                        nums = re.findall(r"[\d,]+", nums_line)
                        if len(nums) >= 9:
                            pos_line = [int(n.replace(",", "")) for n in nums]
                    if "Changes from:" in lines[j]:
                        m = re.search(r"Changes from:\s+(.+?)\s{2,}", lines[j])
                        as_of = m.group(1).strip() if m else ""
                break

        if not pos_line or len(pos_line) < 9:
            return _cache.get("data")

        lev_long = pos_line[6]
        lev_short = pos_line[7]
        total = lev_long + lev_short
        net = lev_long - lev_short
        net_pct = round(net / max(total, 1) * 100, 1)

        if net_pct < -40:
            signal, score = "bullish", 10  # leveraged funds very short → contrarian bullish
        elif net_pct < -20:
            signal, score = "bullish", 5
        elif net_pct > 60:
            signal, score = "bearish", -8  # very long → contrarian bearish
        elif net_pct > 40:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0

        result = {
            "lev_long": lev_long,
            "lev_short": lev_short,
            "net_contracts": net,
            "net_pct": net_pct,
            "signal": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        print(f"[cot] {e}")
        return _cache.get("data")
