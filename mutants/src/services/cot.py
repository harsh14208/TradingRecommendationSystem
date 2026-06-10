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

import logging
import re
import ssl
import time

log = logging.getLogger("signal.trade.cot")

import aiohttp
import certifi

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())
_cache: dict = {"data": None, "ts": 0.0}
CACHE_TTL = 86400 * 4  # 4 days

_URL = "https://www.cftc.gov/dea/futures/financial_lf.htm"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_cot_signal__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_cot_signal__mutmut)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_orig() -> dict | None:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_1() -> dict | None:
    now = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_2() -> dict | None:
    now = time.time()
    if _cache["data"] or now - _cache["ts"] < CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_3() -> dict | None:
    now = time.time()
    if _cache["XXdataXX"] and now - _cache["ts"] < CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_4() -> dict | None:
    now = time.time()
    if _cache["DATA"] and now - _cache["ts"] < CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_5() -> dict | None:
    now = time.time()
    if _cache["data"] and now + _cache["ts"] < CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_6() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["XXtsXX"] < CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_7() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["TS"] < CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_8() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] <= CACHE_TTL:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_9() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["XXdataXX"]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_10() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["DATA"]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_11() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_12() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=None)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_13() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=None) as s:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_14() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(None, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_15() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=None, headers={"User-Agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_16() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers=None) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_17() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_18() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, headers={"User-Agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_19() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), ) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_20() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=None), headers={"User-Agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_21() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=16), headers={"User-Agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_22() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"XXUser-AgentXX": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_23() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"user-agent": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_24() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"USER-AGENT": "Mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_25() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "XXMozilla/5.0XX"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_26() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "mozilla/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_27() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "MOZILLA/5.0"}) as r:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_28() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status == 200:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_29() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status != 201:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_30() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status != 200:
                    return _cache.get(None)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_31() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status != 200:
                    return _cache.get("XXdataXX")
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_32() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status != 200:
                    return _cache.get("DATA")
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_33() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(_URL, timeout=aiohttp.ClientTimeout(total=15), headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status != 200:
                    return _cache.get("data")
                text = None

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_34() -> dict | None:
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

        lines = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_35() -> dict | None:
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

        lines = text.split(None)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_36() -> dict | None:
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

        lines = text.split("XX\nXX")
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_37() -> dict | None:
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
        pos_line = ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_38() -> dict | None:
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
        as_of = None

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_39() -> dict | None:
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
        as_of = "XXXX"

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_40() -> dict | None:
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

        for i, line in enumerate(None):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_41() -> dict | None:
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
            if "E-MINI S&P 500 -" in line.upper() or "SELECT" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_42() -> dict | None:
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
            if "XXE-MINI S&P 500 -XX" in line.upper() and "SELECT" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_43() -> dict | None:
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
            if "e-mini s&p 500 -" in line.upper() and "SELECT" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_44() -> dict | None:
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
            if "E-MINI S&P 500 -" not in line.upper() and "SELECT" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_45() -> dict | None:
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
            if "E-MINI S&P 500 -" in line.lower() and "SELECT" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_46() -> dict | None:
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
            if "E-MINI S&P 500 -" in line.upper() and "XXSELECTXX" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_47() -> dict | None:
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
            if "E-MINI S&P 500 -" in line.upper() and "select" not in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_48() -> dict | None:
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
            if "E-MINI S&P 500 -" in line.upper() and "SELECT" in line.upper():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_49() -> dict | None:
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
            if "E-MINI S&P 500 -" in line.upper() and "SELECT" not in line.lower():
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_50() -> dict | None:
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
                for j in range(None, min(i + 6, len(lines))):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_51() -> dict | None:
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
                for j in range(i, None):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_52() -> dict | None:
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
                for j in range(min(i + 6, len(lines))):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_53() -> dict | None:
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
                for j in range(i, ):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_54() -> dict | None:
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
                for j in range(i, min(None, len(lines))):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_55() -> dict | None:
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
                for j in range(i, min(i + 6, None)):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_56() -> dict | None:
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
                for j in range(i, min(len(lines))):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_57() -> dict | None:
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
                for j in range(i, min(i + 6, )):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_58() -> dict | None:
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
                for j in range(i, min(i - 6, len(lines))):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_59() -> dict | None:
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
                for j in range(i, min(i + 7, len(lines))):
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_60() -> dict | None:
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
                    if "XXPositionsXX" in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_61() -> dict | None:
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
                    if "positions" in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_62() -> dict | None:
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
                    if "POSITIONS" in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_63() -> dict | None:
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
                    if "Positions" not in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_64() -> dict | None:
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
                        nums_line = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_65() -> dict | None:
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
                        nums_line = lines[j - 1] if j + 1 < len(lines) else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_66() -> dict | None:
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
                        nums_line = lines[j + 2] if j + 1 < len(lines) else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_67() -> dict | None:
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
                        nums_line = lines[j + 1] if j - 1 < len(lines) else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_68() -> dict | None:
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
                        nums_line = lines[j + 1] if j + 2 < len(lines) else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_69() -> dict | None:
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
                        nums_line = lines[j + 1] if j + 1 <= len(lines) else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_70() -> dict | None:
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
                        nums_line = lines[j + 1] if j + 1 < len(lines) else "XXXX"
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_71() -> dict | None:
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
                        nums = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_72() -> dict | None:
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
                        nums = re.findall(None, nums_line)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_73() -> dict | None:
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
                        nums = re.findall(r"[\d,]+", None)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_74() -> dict | None:
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
                        nums = re.findall(nums_line)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_75() -> dict | None:
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
                        nums = re.findall(r"[\d,]+", )
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_76() -> dict | None:
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
                        nums = re.findall(r"XX[\d,]+XX", nums_line)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_77() -> dict | None:
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
                        if len(nums) > 9:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_78() -> dict | None:
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
                        if len(nums) >= 10:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_79() -> dict | None:
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
                            pos_line = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_80() -> dict | None:
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
                            pos_line = [int(None) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_81() -> dict | None:
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
                            pos_line = [int(n.replace(None, "")) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_82() -> dict | None:
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
                            pos_line = [int(n.replace(",", None)) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_83() -> dict | None:
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
                            pos_line = [int(n.replace("")) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_84() -> dict | None:
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
                            pos_line = [int(n.replace(",", )) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_85() -> dict | None:
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
                            pos_line = [int(n.replace("XX,XX", "")) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_86() -> dict | None:
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
                            pos_line = [int(n.replace(",", "XXXX")) for n in nums]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_87() -> dict | None:
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
                    if "XXChanges from:XX" in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_88() -> dict | None:
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
                    if "changes from:" in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_89() -> dict | None:
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
                    if "CHANGES FROM:" in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_90() -> dict | None:
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
                    if "Changes from:" not in lines[j]:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_91() -> dict | None:
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
                        m = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_92() -> dict | None:
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
                        m = re.search(None, lines[j])
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_93() -> dict | None:
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
                        m = re.search(r"Changes from:\s+(.+?)\s{2,}", None)
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_94() -> dict | None:
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
                        m = re.search(lines[j])
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_95() -> dict | None:
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
                        m = re.search(r"Changes from:\s+(.+?)\s{2,}", )
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_96() -> dict | None:
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
                        m = re.search(r"XXChanges from:\s+(.+?)\s{2,}XX", lines[j])
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_97() -> dict | None:
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
                        m = re.search(r"changes from:\s+(.+?)\s{2,}", lines[j])
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_98() -> dict | None:
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
                        m = re.search(r"CHANGES FROM:\s+(.+?)\s{2,}", lines[j])
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_99() -> dict | None:
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
                        as_of = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_100() -> dict | None:
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
                        as_of = m.group(None).strip() if m else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_101() -> dict | None:
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
                        as_of = m.group(2).strip() if m else ""
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_102() -> dict | None:
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
                        as_of = m.group(1).strip() if m else "XXXX"
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_103() -> dict | None:
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
                return

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_104() -> dict | None:
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

        if not pos_line and len(pos_line) < 9:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_105() -> dict | None:
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

        if pos_line or len(pos_line) < 9:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_106() -> dict | None:
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

        if not pos_line or len(pos_line) <= 9:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_107() -> dict | None:
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

        if not pos_line or len(pos_line) < 10:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_108() -> dict | None:
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
            return _cache.get(None)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_109() -> dict | None:
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
            return _cache.get("XXdataXX")

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_110() -> dict | None:
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
            return _cache.get("DATA")

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_111() -> dict | None:
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

        lev_long = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_112() -> dict | None:
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

        lev_long = pos_line[7]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_113() -> dict | None:
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
        lev_short = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_114() -> dict | None:
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
        lev_short = pos_line[8]
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_115() -> dict | None:
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
        total = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_116() -> dict | None:
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
        total = lev_long - lev_short
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_117() -> dict | None:
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
        net = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_118() -> dict | None:
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
        net = lev_long + lev_short
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_119() -> dict | None:
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
        net_pct = None

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_120() -> dict | None:
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
        net_pct = round(None, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_121() -> dict | None:
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
        net_pct = round(net / max(total, 1) * 100, None)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_122() -> dict | None:
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
        net_pct = round(1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_123() -> dict | None:
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
        net_pct = round(net / max(total, 1) * 100, )

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_124() -> dict | None:
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
        net_pct = round(net / max(total, 1) / 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_125() -> dict | None:
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
        net_pct = round(net * max(total, 1) * 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_126() -> dict | None:
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
        net_pct = round(net / max(None, 1) * 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_127() -> dict | None:
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
        net_pct = round(net / max(total, None) * 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_128() -> dict | None:
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
        net_pct = round(net / max(1) * 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_129() -> dict | None:
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
        net_pct = round(net / max(total, ) * 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_130() -> dict | None:
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
        net_pct = round(net / max(total, 2) * 100, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_131() -> dict | None:
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
        net_pct = round(net / max(total, 1) * 101, 1)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_132() -> dict | None:
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
        net_pct = round(net / max(total, 1) * 100, 2)

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_133() -> dict | None:
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

        if net_pct <= -40:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_134() -> dict | None:
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

        if net_pct < +40:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_135() -> dict | None:
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

        if net_pct < -41:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_136() -> dict | None:
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
            signal, score = None  # leveraged funds very short → contrarian bullish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_137() -> dict | None:
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
            signal, score = "XXbullishXX", 10  # leveraged funds very short → contrarian bullish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_138() -> dict | None:
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
            signal, score = "BULLISH", 10  # leveraged funds very short → contrarian bullish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_139() -> dict | None:
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
            signal, score = "bullish", 11  # leveraged funds very short → contrarian bullish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_140() -> dict | None:
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
        elif net_pct <= -20:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_141() -> dict | None:
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
        elif net_pct < +20:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_142() -> dict | None:
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
        elif net_pct < -21:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_143() -> dict | None:
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
            signal, score = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_144() -> dict | None:
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
            signal, score = "XXbullishXX", 5
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_145() -> dict | None:
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
            signal, score = "BULLISH", 5
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_146() -> dict | None:
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
            signal, score = "bullish", 6
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_147() -> dict | None:
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
        elif net_pct >= 60:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_148() -> dict | None:
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
        elif net_pct > 61:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_149() -> dict | None:
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
            signal, score = None  # very long → contrarian bearish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_150() -> dict | None:
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
            signal, score = "XXbearishXX", -8  # very long → contrarian bearish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_151() -> dict | None:
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
            signal, score = "BEARISH", -8  # very long → contrarian bearish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_152() -> dict | None:
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
            signal, score = "bearish", +8  # very long → contrarian bearish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_153() -> dict | None:
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
            signal, score = "bearish", -9  # very long → contrarian bearish
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_154() -> dict | None:
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
        elif net_pct >= 40:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_155() -> dict | None:
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
        elif net_pct > 41:
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_156() -> dict | None:
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
            signal, score = None
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_157() -> dict | None:
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
            signal, score = "XXbearishXX", -4
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_158() -> dict | None:
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
            signal, score = "BEARISH", -4
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_159() -> dict | None:
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
            signal, score = "bearish", +4
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_160() -> dict | None:
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
            signal, score = "bearish", -5
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_161() -> dict | None:
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
            signal, score = None

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_162() -> dict | None:
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
            signal, score = "XXneutralXX", 0

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_163() -> dict | None:
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
            signal, score = "NEUTRAL", 0

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_164() -> dict | None:
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
            signal, score = "neutral", 1

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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_165() -> dict | None:
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

        result = None
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_166() -> dict | None:
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
            "XXlev_longXX": lev_long,
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_167() -> dict | None:
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
            "LEV_LONG": lev_long,
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_168() -> dict | None:
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
            "XXlev_shortXX": lev_short,
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_169() -> dict | None:
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
            "LEV_SHORT": lev_short,
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
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_170() -> dict | None:
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
            "XXnet_contractsXX": net,
            "net_pct": net_pct,
            "signal": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_171() -> dict | None:
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
            "NET_CONTRACTS": net,
            "net_pct": net_pct,
            "signal": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_172() -> dict | None:
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
            "XXnet_pctXX": net_pct,
            "signal": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_173() -> dict | None:
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
            "NET_PCT": net_pct,
            "signal": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_174() -> dict | None:
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
            "XXsignalXX": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_175() -> dict | None:
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
            "SIGNAL": signal,
            "score": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_176() -> dict | None:
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
            "XXscoreXX": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_177() -> dict | None:
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
            "SCORE": score,
            "as_of": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_178() -> dict | None:
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
            "XXas_ofXX": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_179() -> dict | None:
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
            "AS_OF": as_of,
        }
        _cache["data"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_180() -> dict | None:
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
        _cache["data"] = None
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_181() -> dict | None:
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
        _cache["XXdataXX"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_182() -> dict | None:
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
        _cache["DATA"] = result
        _cache["ts"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_183() -> dict | None:
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
        _cache["ts"] = None
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_184() -> dict | None:
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
        _cache["XXtsXX"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_185() -> dict | None:
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
        _cache["TS"] = now
        return result
    except Exception as e:
        log.warning(f"[cot] {e}")
        return _cache.get("data")


async def x_get_cot_signal__mutmut_186() -> dict | None:
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
        log.warning(None)
        return _cache.get("data")


async def x_get_cot_signal__mutmut_187() -> dict | None:
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
        log.warning(f"[cot] {e}")
        return _cache.get(None)


async def x_get_cot_signal__mutmut_188() -> dict | None:
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
        log.warning(f"[cot] {e}")
        return _cache.get("XXdataXX")


async def x_get_cot_signal__mutmut_189() -> dict | None:
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
        log.warning(f"[cot] {e}")
        return _cache.get("DATA")

mutants_x_get_cot_signal__mutmut['_mutmut_orig'] = x_get_cot_signal__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_1'] = x_get_cot_signal__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_2'] = x_get_cot_signal__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_3'] = x_get_cot_signal__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_4'] = x_get_cot_signal__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_5'] = x_get_cot_signal__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_6'] = x_get_cot_signal__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_7'] = x_get_cot_signal__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_8'] = x_get_cot_signal__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_9'] = x_get_cot_signal__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_10'] = x_get_cot_signal__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_11'] = x_get_cot_signal__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_12'] = x_get_cot_signal__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_13'] = x_get_cot_signal__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_14'] = x_get_cot_signal__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_15'] = x_get_cot_signal__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_16'] = x_get_cot_signal__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_17'] = x_get_cot_signal__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_18'] = x_get_cot_signal__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_19'] = x_get_cot_signal__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_20'] = x_get_cot_signal__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_21'] = x_get_cot_signal__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_22'] = x_get_cot_signal__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_23'] = x_get_cot_signal__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_24'] = x_get_cot_signal__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_25'] = x_get_cot_signal__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_26'] = x_get_cot_signal__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_27'] = x_get_cot_signal__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_28'] = x_get_cot_signal__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_29'] = x_get_cot_signal__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_30'] = x_get_cot_signal__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_31'] = x_get_cot_signal__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_32'] = x_get_cot_signal__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_33'] = x_get_cot_signal__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_34'] = x_get_cot_signal__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_35'] = x_get_cot_signal__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_36'] = x_get_cot_signal__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_37'] = x_get_cot_signal__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_38'] = x_get_cot_signal__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_39'] = x_get_cot_signal__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_40'] = x_get_cot_signal__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_41'] = x_get_cot_signal__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_42'] = x_get_cot_signal__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_43'] = x_get_cot_signal__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_44'] = x_get_cot_signal__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_45'] = x_get_cot_signal__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_46'] = x_get_cot_signal__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_47'] = x_get_cot_signal__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_48'] = x_get_cot_signal__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_49'] = x_get_cot_signal__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_50'] = x_get_cot_signal__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_51'] = x_get_cot_signal__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_52'] = x_get_cot_signal__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_53'] = x_get_cot_signal__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_54'] = x_get_cot_signal__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_55'] = x_get_cot_signal__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_56'] = x_get_cot_signal__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_57'] = x_get_cot_signal__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_58'] = x_get_cot_signal__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_59'] = x_get_cot_signal__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_60'] = x_get_cot_signal__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_61'] = x_get_cot_signal__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_62'] = x_get_cot_signal__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_63'] = x_get_cot_signal__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_64'] = x_get_cot_signal__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_65'] = x_get_cot_signal__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_66'] = x_get_cot_signal__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_67'] = x_get_cot_signal__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_68'] = x_get_cot_signal__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_69'] = x_get_cot_signal__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_70'] = x_get_cot_signal__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_71'] = x_get_cot_signal__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_72'] = x_get_cot_signal__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_73'] = x_get_cot_signal__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_74'] = x_get_cot_signal__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_75'] = x_get_cot_signal__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_76'] = x_get_cot_signal__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_77'] = x_get_cot_signal__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_78'] = x_get_cot_signal__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_79'] = x_get_cot_signal__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_80'] = x_get_cot_signal__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_81'] = x_get_cot_signal__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_82'] = x_get_cot_signal__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_83'] = x_get_cot_signal__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_84'] = x_get_cot_signal__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_85'] = x_get_cot_signal__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_86'] = x_get_cot_signal__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_87'] = x_get_cot_signal__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_88'] = x_get_cot_signal__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_89'] = x_get_cot_signal__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_90'] = x_get_cot_signal__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_91'] = x_get_cot_signal__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_92'] = x_get_cot_signal__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_93'] = x_get_cot_signal__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_94'] = x_get_cot_signal__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_95'] = x_get_cot_signal__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_96'] = x_get_cot_signal__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_97'] = x_get_cot_signal__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_98'] = x_get_cot_signal__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_99'] = x_get_cot_signal__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_100'] = x_get_cot_signal__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_101'] = x_get_cot_signal__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_102'] = x_get_cot_signal__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_103'] = x_get_cot_signal__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_104'] = x_get_cot_signal__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_105'] = x_get_cot_signal__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_106'] = x_get_cot_signal__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_107'] = x_get_cot_signal__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_108'] = x_get_cot_signal__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_109'] = x_get_cot_signal__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_110'] = x_get_cot_signal__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_111'] = x_get_cot_signal__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_112'] = x_get_cot_signal__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_113'] = x_get_cot_signal__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_114'] = x_get_cot_signal__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_115'] = x_get_cot_signal__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_116'] = x_get_cot_signal__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_117'] = x_get_cot_signal__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_118'] = x_get_cot_signal__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_119'] = x_get_cot_signal__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_120'] = x_get_cot_signal__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_121'] = x_get_cot_signal__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_122'] = x_get_cot_signal__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_123'] = x_get_cot_signal__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_124'] = x_get_cot_signal__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_125'] = x_get_cot_signal__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_126'] = x_get_cot_signal__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_127'] = x_get_cot_signal__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_128'] = x_get_cot_signal__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_129'] = x_get_cot_signal__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_130'] = x_get_cot_signal__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_131'] = x_get_cot_signal__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_132'] = x_get_cot_signal__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_133'] = x_get_cot_signal__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_134'] = x_get_cot_signal__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_135'] = x_get_cot_signal__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_136'] = x_get_cot_signal__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_137'] = x_get_cot_signal__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_138'] = x_get_cot_signal__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_139'] = x_get_cot_signal__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_140'] = x_get_cot_signal__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_141'] = x_get_cot_signal__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_142'] = x_get_cot_signal__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_143'] = x_get_cot_signal__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_144'] = x_get_cot_signal__mutmut_144 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_145'] = x_get_cot_signal__mutmut_145 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_146'] = x_get_cot_signal__mutmut_146 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_147'] = x_get_cot_signal__mutmut_147 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_148'] = x_get_cot_signal__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_149'] = x_get_cot_signal__mutmut_149 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_150'] = x_get_cot_signal__mutmut_150 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_151'] = x_get_cot_signal__mutmut_151 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_152'] = x_get_cot_signal__mutmut_152 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_153'] = x_get_cot_signal__mutmut_153 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_154'] = x_get_cot_signal__mutmut_154 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_155'] = x_get_cot_signal__mutmut_155 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_156'] = x_get_cot_signal__mutmut_156 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_157'] = x_get_cot_signal__mutmut_157 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_158'] = x_get_cot_signal__mutmut_158 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_159'] = x_get_cot_signal__mutmut_159 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_160'] = x_get_cot_signal__mutmut_160 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_161'] = x_get_cot_signal__mutmut_161 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_162'] = x_get_cot_signal__mutmut_162 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_163'] = x_get_cot_signal__mutmut_163 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_164'] = x_get_cot_signal__mutmut_164 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_165'] = x_get_cot_signal__mutmut_165 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_166'] = x_get_cot_signal__mutmut_166 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_167'] = x_get_cot_signal__mutmut_167 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_168'] = x_get_cot_signal__mutmut_168 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_169'] = x_get_cot_signal__mutmut_169 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_170'] = x_get_cot_signal__mutmut_170 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_171'] = x_get_cot_signal__mutmut_171 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_172'] = x_get_cot_signal__mutmut_172 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_173'] = x_get_cot_signal__mutmut_173 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_174'] = x_get_cot_signal__mutmut_174 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_175'] = x_get_cot_signal__mutmut_175 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_176'] = x_get_cot_signal__mutmut_176 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_177'] = x_get_cot_signal__mutmut_177 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_178'] = x_get_cot_signal__mutmut_178 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_179'] = x_get_cot_signal__mutmut_179 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_180'] = x_get_cot_signal__mutmut_180 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_181'] = x_get_cot_signal__mutmut_181 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_182'] = x_get_cot_signal__mutmut_182 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_183'] = x_get_cot_signal__mutmut_183 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_184'] = x_get_cot_signal__mutmut_184 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_185'] = x_get_cot_signal__mutmut_185 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_186'] = x_get_cot_signal__mutmut_186 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_187'] = x_get_cot_signal__mutmut_187 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_188'] = x_get_cot_signal__mutmut_188 # type: ignore # mutmut generated
mutants_x_get_cot_signal__mutmut['x_get_cot_signal__mutmut_189'] = x_get_cot_signal__mutmut_189 # type: ignore # mutmut generated
