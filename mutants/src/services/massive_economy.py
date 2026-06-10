"""
Massive Economy API — Treasury Yields, Inflation, Labor Market

Replaces FRED API calls in macro.py. No FRED key required.
Provides: yield curve (2Y, 10Y, 30Y), CPI, PCE, Unemployment, NFP.

Used as augment/fallback to existing macro.py.
Cache: 1 hour.
"""

import asyncio
import logging
import os
import time

import aiohttp

log = logging.getLogger("signal.trade.massive_economy")

_cache: dict = {"data": None, "ts": 0.0}
_TTL = 3600

_BASE = "https://api.polygon.io"


import ssl as _ssl

import certifi as _certifi
from services.http_client import shared_session

_SSL_CTX = _ssl.create_default_context(cafile=_certifi.where())


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch__mutmut)
async def _fetch(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_orig(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_1(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            None, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_2(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=None, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_3(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=None, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_4(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=None
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_5(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_6(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_7(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_8(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_9(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=None)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_10(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=9)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_11(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status == 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_12(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 201:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_13(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = None
            return d.get("results") or []
    except Exception:
        return []


async def x__fetch__mutmut_14(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("results") and []
    except Exception:
        return []


async def x__fetch__mutmut_15(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get(None) or []
    except Exception:
        return []


async def x__fetch__mutmut_16(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("XXresultsXX") or []
    except Exception:
        return []


async def x__fetch__mutmut_17(session, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:  # 403 = premium endpoint, degrade gracefully
                return []
            d = await resp.json()
            return d.get("RESULTS") or []
    except Exception:
        return []

mutants_x__fetch__mutmut['_mutmut_orig'] = x__fetch__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_1'] = x__fetch__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_2'] = x__fetch__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_3'] = x__fetch__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_4'] = x__fetch__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_5'] = x__fetch__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_6'] = x__fetch__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_7'] = x__fetch__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_8'] = x__fetch__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_9'] = x__fetch__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_10'] = x__fetch__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_11'] = x__fetch__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_12'] = x__fetch__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_13'] = x__fetch__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_14'] = x__fetch__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_15'] = x__fetch__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_16'] = x__fetch__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch__mutmut['x__fetch__mutmut_17'] = x__fetch__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_economy_data__mutmut)
async def get_economy_data() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_orig() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_1() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = None
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_2() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None or now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_3() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["XXdataXX"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_4() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["DATA"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_5() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_6() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now + _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_7() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["XXtsXX"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_8() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["TS"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_9() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] <= _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_10() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["XXdataXX"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_11() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["DATA"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_12() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = None
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_13() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv(None)
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_14() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("XXMASSIVE_API_KEYXX")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_15() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("massive_api_key")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_16() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_17() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = None
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_18() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"XXapiKeyXX": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_19() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apikey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_20() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"APIKEY": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_21() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "XXlimitXX": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_22() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "LIMIT": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_23() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 6}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_24() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = None

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_25() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            None,
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_26() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            None,
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_27() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            None,
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_28() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=None,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_29() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_30() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_31() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_32() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_33() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(None, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_34() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, None, base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_35() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", None),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_36() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch("economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_37() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_38() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", ),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_39() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "XXeconomy/treasury_yieldsXX", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_40() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "ECONOMY/TREASURY_YIELDS", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_41() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(None, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_42() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, None, base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_43() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", None),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_44() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch("economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_45() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_46() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", ),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_47() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "XXeconomy/inflationXX", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_48() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "ECONOMY/INFLATION", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_49() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(None, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_50() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, None, base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_51() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", None),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_52() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch("economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_53() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_54() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", ),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_55() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "XXeconomy/labor_marketXX", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_56() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "ECONOMY/LABOR_MARKET", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_57() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=False,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_58() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = None

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_59() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) or yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_60() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = None
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_61() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[1]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_62() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = None
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_63() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") and latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_64() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get(None) or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_65() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("XXyield_2yXX") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_66() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("YIELD_2Y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_67() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get(None)
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_68() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("XXtwo_yearXX")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_69() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("TWO_YEAR")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_70() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = None
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_71() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") and latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_72() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get(None) or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_73() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("XXyield_10yXX") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_74() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("YIELD_10Y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_75() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get(None)
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_76() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("XXten_yearXX")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_77() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("TEN_YEAR")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_78() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = None
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_79() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") and latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_80() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get(None) or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_81() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("XXyield_30yXX") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_82() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("YIELD_30Y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_83() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get(None)
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_84() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("XXthirty_yearXX")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_85() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("THIRTY_YEAR")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_86() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_87() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = None
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_88() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["XXyield_2yXX"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_89() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["YIELD_2Y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_90() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(None, 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_91() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), None)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_92() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_93() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), )
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_94() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(None), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_95() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 4)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_96() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_97() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = None
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_98() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["XXyield_10yXX"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_99() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["YIELD_10Y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_100() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(None, 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_101() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), None)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_102() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_103() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), )
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_104() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(None), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_105() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 4)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_106() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_107() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = None
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_108() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["XXyield_30yXX"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_109() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["YIELD_30Y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_110() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(None, 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_111() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), None)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_112() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_113() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), )
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_114() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(None), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_115() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 4)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_116() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 or y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_117() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = None

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_118() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["XXyc_spread_massiveXX"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_119() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["YC_SPREAD_MASSIVE"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_120() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(None, 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_121() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), None)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_122() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_123() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), )

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_124() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) + float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_125() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(None) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_126() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(None), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_127() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 4)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_128() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) or inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_129() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = None
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_130() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[1]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_131() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = None
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_132() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") and latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_133() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get(None) or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_134() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("XXcpi_yoyXX") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_135() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("CPI_YOY") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_136() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get(None)
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_137() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("XXcpi_annualXX")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_138() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("CPI_ANNUAL")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_139() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = None
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_140() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") and latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_141() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get(None) or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_142() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("XXpce_yoyXX") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_143() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("PCE_YOY") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_144() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get(None)
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_145() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("XXpce_annualXX")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_146() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("PCE_ANNUAL")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_147() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_148() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = None
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_149() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["XXcpi_yoyXX"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_150() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["CPI_YOY"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_151() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(None, 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_152() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), None)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_153() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_154() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), )
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_155() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(None), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_156() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 3)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_157() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_158() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = None

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_159() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["XXpce_yoyXX"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_160() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["PCE_YOY"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_161() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(None, 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_162() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), None)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_163() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_164() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), )

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_165() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(None), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_166() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 3)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_167() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) or labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_168() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = None
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_169() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[1]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_170() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = None
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_171() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") and latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_172() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get(None) or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_173() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("XXunemployment_rateXX") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_174() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("UNEMPLOYMENT_RATE") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_175() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get(None)
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_176() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("XXunemploymentXX")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_177() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("UNEMPLOYMENT")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_178() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = None
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_179() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") and latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_180() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get(None) or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_181() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("XXnonfarm_payrollsXX") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_182() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("NONFARM_PAYROLLS") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_183() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get(None)
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_184() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("XXpayrolls_changeXX")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_185() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("PAYROLLS_CHANGE")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_186() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_187() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = None
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_188() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["XXunemploymentXX"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_189() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["UNEMPLOYMENT"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_190() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(None, 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_191() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), None)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_192() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_193() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), )
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_194() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(None), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_195() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 3)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_196() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_197() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = None

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_198() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["XXnfp_change_kXX"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_199() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["NFP_CHANGE_K"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_200() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(None, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_201() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, None)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_202() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_203() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, )

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_204() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) * 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_205() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(None) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_206() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1001, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_207() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 2)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_208() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = None
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_209() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["XXdataXX"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_210() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["DATA"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_211() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = None
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_212() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["XXtsXX"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_213() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["TS"] = now
    log.info(f"[massive_economy] fetched: {list(result.keys())}")
    return result


async def x_get_economy_data__mutmut_214() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(None)
    return result


async def x_get_economy_data__mutmut_215() -> dict:
    """
    Fetch macro indicators from Massive Economy endpoints.
    Returns normalised dict compatible with macro.py output.
    """
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base = {"apiKey": api_key, "limit": 5}
    async with shared_session() as session:
        yields_raw, inflation_raw, labor_raw = await asyncio.gather(
            _fetch(session, "economy/treasury_yields", base),
            _fetch(session, "economy/inflation", base),
            _fetch(session, "economy/labor_market", base),
            return_exceptions=True,
        )

    result: dict = {}

    # ── Treasury Yields ───────────────────────────────────────────────────────
    if isinstance(yields_raw, list) and yields_raw:
        latest = yields_raw[0]
        y2 = latest.get("yield_2y") or latest.get("two_year")
        y10 = latest.get("yield_10y") or latest.get("ten_year")
        y30 = latest.get("yield_30y") or latest.get("thirty_year")
        if y2 is not None:
            result["yield_2y"] = round(float(y2), 3)
        if y10 is not None:
            result["yield_10y"] = round(float(y10), 3)
        if y30 is not None:
            result["yield_30y"] = round(float(y30), 3)
        if y2 and y10:
            result["yc_spread_massive"] = round(float(y10) - float(y2), 3)

    # ── Inflation ─────────────────────────────────────────────────────────────
    if isinstance(inflation_raw, list) and inflation_raw:
        latest = inflation_raw[0]
        cpi = latest.get("cpi_yoy") or latest.get("cpi_annual")
        pce = latest.get("pce_yoy") or latest.get("pce_annual")
        if cpi is not None:
            result["cpi_yoy"] = round(float(cpi), 2)
        if pce is not None:
            result["pce_yoy"] = round(float(pce), 2)

    # ── Labor Market ──────────────────────────────────────────────────────────
    if isinstance(labor_raw, list) and labor_raw:
        latest = labor_raw[0]
        ue = latest.get("unemployment_rate") or latest.get("unemployment")
        nfp = latest.get("nonfarm_payrolls") or latest.get("payrolls_change")
        if ue is not None:
            result["unemployment"] = round(float(ue), 2)
        if nfp is not None:
            result["nfp_change_k"] = round(float(nfp) / 1000, 1)

    _cache["data"] = result
    _cache["ts"] = now
    log.info(f"[massive_economy] fetched: {list(None)}")
    return result

mutants_x_get_economy_data__mutmut['_mutmut_orig'] = x_get_economy_data__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_1'] = x_get_economy_data__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_2'] = x_get_economy_data__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_3'] = x_get_economy_data__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_4'] = x_get_economy_data__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_5'] = x_get_economy_data__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_6'] = x_get_economy_data__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_7'] = x_get_economy_data__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_8'] = x_get_economy_data__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_9'] = x_get_economy_data__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_10'] = x_get_economy_data__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_11'] = x_get_economy_data__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_12'] = x_get_economy_data__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_13'] = x_get_economy_data__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_14'] = x_get_economy_data__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_15'] = x_get_economy_data__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_16'] = x_get_economy_data__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_17'] = x_get_economy_data__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_18'] = x_get_economy_data__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_19'] = x_get_economy_data__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_20'] = x_get_economy_data__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_21'] = x_get_economy_data__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_22'] = x_get_economy_data__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_23'] = x_get_economy_data__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_24'] = x_get_economy_data__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_25'] = x_get_economy_data__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_26'] = x_get_economy_data__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_27'] = x_get_economy_data__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_28'] = x_get_economy_data__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_29'] = x_get_economy_data__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_30'] = x_get_economy_data__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_31'] = x_get_economy_data__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_32'] = x_get_economy_data__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_33'] = x_get_economy_data__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_34'] = x_get_economy_data__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_35'] = x_get_economy_data__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_36'] = x_get_economy_data__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_37'] = x_get_economy_data__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_38'] = x_get_economy_data__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_39'] = x_get_economy_data__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_40'] = x_get_economy_data__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_41'] = x_get_economy_data__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_42'] = x_get_economy_data__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_43'] = x_get_economy_data__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_44'] = x_get_economy_data__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_45'] = x_get_economy_data__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_46'] = x_get_economy_data__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_47'] = x_get_economy_data__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_48'] = x_get_economy_data__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_49'] = x_get_economy_data__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_50'] = x_get_economy_data__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_51'] = x_get_economy_data__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_52'] = x_get_economy_data__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_53'] = x_get_economy_data__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_54'] = x_get_economy_data__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_55'] = x_get_economy_data__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_56'] = x_get_economy_data__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_57'] = x_get_economy_data__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_58'] = x_get_economy_data__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_59'] = x_get_economy_data__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_60'] = x_get_economy_data__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_61'] = x_get_economy_data__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_62'] = x_get_economy_data__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_63'] = x_get_economy_data__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_64'] = x_get_economy_data__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_65'] = x_get_economy_data__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_66'] = x_get_economy_data__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_67'] = x_get_economy_data__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_68'] = x_get_economy_data__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_69'] = x_get_economy_data__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_70'] = x_get_economy_data__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_71'] = x_get_economy_data__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_72'] = x_get_economy_data__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_73'] = x_get_economy_data__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_74'] = x_get_economy_data__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_75'] = x_get_economy_data__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_76'] = x_get_economy_data__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_77'] = x_get_economy_data__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_78'] = x_get_economy_data__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_79'] = x_get_economy_data__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_80'] = x_get_economy_data__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_81'] = x_get_economy_data__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_82'] = x_get_economy_data__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_83'] = x_get_economy_data__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_84'] = x_get_economy_data__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_85'] = x_get_economy_data__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_86'] = x_get_economy_data__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_87'] = x_get_economy_data__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_88'] = x_get_economy_data__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_89'] = x_get_economy_data__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_90'] = x_get_economy_data__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_91'] = x_get_economy_data__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_92'] = x_get_economy_data__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_93'] = x_get_economy_data__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_94'] = x_get_economy_data__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_95'] = x_get_economy_data__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_96'] = x_get_economy_data__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_97'] = x_get_economy_data__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_98'] = x_get_economy_data__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_99'] = x_get_economy_data__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_100'] = x_get_economy_data__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_101'] = x_get_economy_data__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_102'] = x_get_economy_data__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_103'] = x_get_economy_data__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_104'] = x_get_economy_data__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_105'] = x_get_economy_data__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_106'] = x_get_economy_data__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_107'] = x_get_economy_data__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_108'] = x_get_economy_data__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_109'] = x_get_economy_data__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_110'] = x_get_economy_data__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_111'] = x_get_economy_data__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_112'] = x_get_economy_data__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_113'] = x_get_economy_data__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_114'] = x_get_economy_data__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_115'] = x_get_economy_data__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_116'] = x_get_economy_data__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_117'] = x_get_economy_data__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_118'] = x_get_economy_data__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_119'] = x_get_economy_data__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_120'] = x_get_economy_data__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_121'] = x_get_economy_data__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_122'] = x_get_economy_data__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_123'] = x_get_economy_data__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_124'] = x_get_economy_data__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_125'] = x_get_economy_data__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_126'] = x_get_economy_data__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_127'] = x_get_economy_data__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_128'] = x_get_economy_data__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_129'] = x_get_economy_data__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_130'] = x_get_economy_data__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_131'] = x_get_economy_data__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_132'] = x_get_economy_data__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_133'] = x_get_economy_data__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_134'] = x_get_economy_data__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_135'] = x_get_economy_data__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_136'] = x_get_economy_data__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_137'] = x_get_economy_data__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_138'] = x_get_economy_data__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_139'] = x_get_economy_data__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_140'] = x_get_economy_data__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_141'] = x_get_economy_data__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_142'] = x_get_economy_data__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_143'] = x_get_economy_data__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_144'] = x_get_economy_data__mutmut_144 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_145'] = x_get_economy_data__mutmut_145 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_146'] = x_get_economy_data__mutmut_146 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_147'] = x_get_economy_data__mutmut_147 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_148'] = x_get_economy_data__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_149'] = x_get_economy_data__mutmut_149 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_150'] = x_get_economy_data__mutmut_150 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_151'] = x_get_economy_data__mutmut_151 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_152'] = x_get_economy_data__mutmut_152 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_153'] = x_get_economy_data__mutmut_153 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_154'] = x_get_economy_data__mutmut_154 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_155'] = x_get_economy_data__mutmut_155 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_156'] = x_get_economy_data__mutmut_156 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_157'] = x_get_economy_data__mutmut_157 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_158'] = x_get_economy_data__mutmut_158 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_159'] = x_get_economy_data__mutmut_159 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_160'] = x_get_economy_data__mutmut_160 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_161'] = x_get_economy_data__mutmut_161 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_162'] = x_get_economy_data__mutmut_162 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_163'] = x_get_economy_data__mutmut_163 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_164'] = x_get_economy_data__mutmut_164 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_165'] = x_get_economy_data__mutmut_165 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_166'] = x_get_economy_data__mutmut_166 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_167'] = x_get_economy_data__mutmut_167 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_168'] = x_get_economy_data__mutmut_168 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_169'] = x_get_economy_data__mutmut_169 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_170'] = x_get_economy_data__mutmut_170 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_171'] = x_get_economy_data__mutmut_171 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_172'] = x_get_economy_data__mutmut_172 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_173'] = x_get_economy_data__mutmut_173 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_174'] = x_get_economy_data__mutmut_174 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_175'] = x_get_economy_data__mutmut_175 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_176'] = x_get_economy_data__mutmut_176 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_177'] = x_get_economy_data__mutmut_177 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_178'] = x_get_economy_data__mutmut_178 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_179'] = x_get_economy_data__mutmut_179 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_180'] = x_get_economy_data__mutmut_180 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_181'] = x_get_economy_data__mutmut_181 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_182'] = x_get_economy_data__mutmut_182 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_183'] = x_get_economy_data__mutmut_183 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_184'] = x_get_economy_data__mutmut_184 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_185'] = x_get_economy_data__mutmut_185 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_186'] = x_get_economy_data__mutmut_186 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_187'] = x_get_economy_data__mutmut_187 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_188'] = x_get_economy_data__mutmut_188 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_189'] = x_get_economy_data__mutmut_189 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_190'] = x_get_economy_data__mutmut_190 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_191'] = x_get_economy_data__mutmut_191 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_192'] = x_get_economy_data__mutmut_192 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_193'] = x_get_economy_data__mutmut_193 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_194'] = x_get_economy_data__mutmut_194 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_195'] = x_get_economy_data__mutmut_195 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_196'] = x_get_economy_data__mutmut_196 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_197'] = x_get_economy_data__mutmut_197 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_198'] = x_get_economy_data__mutmut_198 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_199'] = x_get_economy_data__mutmut_199 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_200'] = x_get_economy_data__mutmut_200 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_201'] = x_get_economy_data__mutmut_201 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_202'] = x_get_economy_data__mutmut_202 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_203'] = x_get_economy_data__mutmut_203 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_204'] = x_get_economy_data__mutmut_204 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_205'] = x_get_economy_data__mutmut_205 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_206'] = x_get_economy_data__mutmut_206 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_207'] = x_get_economy_data__mutmut_207 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_208'] = x_get_economy_data__mutmut_208 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_209'] = x_get_economy_data__mutmut_209 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_210'] = x_get_economy_data__mutmut_210 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_211'] = x_get_economy_data__mutmut_211 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_212'] = x_get_economy_data__mutmut_212 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_213'] = x_get_economy_data__mutmut_213 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_214'] = x_get_economy_data__mutmut_214 # type: ignore # mutmut generated
mutants_x_get_economy_data__mutmut['x_get_economy_data__mutmut_215'] = x_get_economy_data__mutmut_215 # type: ignore # mutmut generated
