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
