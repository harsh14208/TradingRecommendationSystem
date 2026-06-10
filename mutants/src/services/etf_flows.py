"""
ETF Fund Flows — Massive Partners API

Tracks net capital inflows/outflows for sector ETFs (XLK, XLF, XLE…).
Strong inflows → institutional rotation into sector → bullish for constituents.
Strong outflows → institutional exit → bearish for constituents.

Signal value:
  • ETF 5-day net flow > +$500M  → +4 pts for all stocks in that sector
  • ETF 5-day net flow < -$500M  → −4 pts for all stocks in that sector
  • Scaled proportionally for in-between values

Sector ETF → constituent mapping via services/sector.py SECTOR_MAP.
4-hour cache.
"""

import asyncio
import logging
import os
import time

import aiohttp
from services.http_client import get_ssl_context, shared_session

log = logging.getLogger("signal.trade.etf_flows")

_cache: dict = {"data": None, "ts": 0.0}
_TTL = 1800  # 30 minutes — ETF flow data via Polygon (unlimited calls)

SECTOR_ETFS = ["XLK", "XLF", "XLY", "XLC", "XLV", "XLP", "XLE", "XLI", "XLB", "XLRE", "XLU"]

_BASE = "https://api.polygon.io"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch_etf_flows_massive__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_etf_flows_massive__mutmut)
async def _fetch_etf_flows_massive(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_orig(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_1(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = None
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_2(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv(None)
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_3(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("XXMASSIVE_API_KEYXX")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_4(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("massive_api_key")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_5(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_6(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = None
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_7(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = None
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_8(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = None
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_9(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = None
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_10(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"XXapiKeyXX": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_11(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apikey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_12(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"APIKEY": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_13(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "XXtickerXX": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_14(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "TICKER": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_15(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "XXlimitXX": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_16(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "LIMIT": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_17(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 11}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_18(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        None, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_19(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=None, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_20(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=None, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_21(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=None
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_22(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_23(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_24(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_25(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_26(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=None)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_27(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=9)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_28(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status == 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_29(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 201:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_30(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = None
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_31(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = None
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_32(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") and []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_33(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get(None) or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_34(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("XXresultsXX") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_35(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("RESULTS") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_36(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_37(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = None
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_38(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(None)
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_39(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) and 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_40(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get(None, 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_41(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", None) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_42(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get(0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_43(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", ) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_44(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("XXfund_flowXX", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_45(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("FUND_FLOW", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_46(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 1) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_47(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 1 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_48(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:6])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_49(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = None
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_50(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get(None, 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_51(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", None) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_52(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get(0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_53(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", ) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_54(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[1].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_55(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("XXfund_flowXX", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_56(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("FUND_FLOW", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_57(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 1) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_58(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 1
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_59(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = None
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_60(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "XXflow_5d_mXX": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_61(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "FLOW_5D_M": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_62(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(None, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_63(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, None),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_64(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_65(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, ),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_66(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d * 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_67(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1000001, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_68(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 2),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_69(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "XXflow_1d_mXX": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_70(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "FLOW_1D_M": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_71(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(None, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_72(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, None),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_73(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_74(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, ),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_75(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d * 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_76(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1000001, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_77(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 2),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_78(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "XXtrendXX": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_79(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "TREND": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_80(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "XXinflowXX" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_81(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "INFLOW" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_82(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d >= 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_83(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 1 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_84(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "XXoutflowXX",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_85(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "OUTFLOW",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_86(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(None) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


async def x__fetch_etf_flows_massive__mutmut_87(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    ssl_ctx = get_ssl_context()
    results: dict[str, dict] = {}
    try:
        async with shared_session() as session:

            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(
                        url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)
                    ) as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        rows = data.get("results") or []
                        if not rows:
                            return
                        # rows are newest-first; sum last 5 trading days
                        flow_5d = sum(r.get("fund_flow", 0) or 0 for r in rows[:5])
                        flow_1d = rows[0].get("fund_flow", 0) if rows else 0
                        results[etf] = {
                            "flow_5d_m": round(flow_5d / 1_000_000, 1),  # convert to $M
                            "flow_1d_m": round(flow_1d / 1_000_000, 1),
                            "trend": "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(None)

    return results

mutants_x__fetch_etf_flows_massive__mutmut['_mutmut_orig'] = x__fetch_etf_flows_massive__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_1'] = x__fetch_etf_flows_massive__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_2'] = x__fetch_etf_flows_massive__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_3'] = x__fetch_etf_flows_massive__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_4'] = x__fetch_etf_flows_massive__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_5'] = x__fetch_etf_flows_massive__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_6'] = x__fetch_etf_flows_massive__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_7'] = x__fetch_etf_flows_massive__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_8'] = x__fetch_etf_flows_massive__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_9'] = x__fetch_etf_flows_massive__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_10'] = x__fetch_etf_flows_massive__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_11'] = x__fetch_etf_flows_massive__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_12'] = x__fetch_etf_flows_massive__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_13'] = x__fetch_etf_flows_massive__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_14'] = x__fetch_etf_flows_massive__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_15'] = x__fetch_etf_flows_massive__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_16'] = x__fetch_etf_flows_massive__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_17'] = x__fetch_etf_flows_massive__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_18'] = x__fetch_etf_flows_massive__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_19'] = x__fetch_etf_flows_massive__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_20'] = x__fetch_etf_flows_massive__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_21'] = x__fetch_etf_flows_massive__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_22'] = x__fetch_etf_flows_massive__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_23'] = x__fetch_etf_flows_massive__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_24'] = x__fetch_etf_flows_massive__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_25'] = x__fetch_etf_flows_massive__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_26'] = x__fetch_etf_flows_massive__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_27'] = x__fetch_etf_flows_massive__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_28'] = x__fetch_etf_flows_massive__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_29'] = x__fetch_etf_flows_massive__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_30'] = x__fetch_etf_flows_massive__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_31'] = x__fetch_etf_flows_massive__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_32'] = x__fetch_etf_flows_massive__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_33'] = x__fetch_etf_flows_massive__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_34'] = x__fetch_etf_flows_massive__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_35'] = x__fetch_etf_flows_massive__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_36'] = x__fetch_etf_flows_massive__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_37'] = x__fetch_etf_flows_massive__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_38'] = x__fetch_etf_flows_massive__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_39'] = x__fetch_etf_flows_massive__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_40'] = x__fetch_etf_flows_massive__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_41'] = x__fetch_etf_flows_massive__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_42'] = x__fetch_etf_flows_massive__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_43'] = x__fetch_etf_flows_massive__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_44'] = x__fetch_etf_flows_massive__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_45'] = x__fetch_etf_flows_massive__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_46'] = x__fetch_etf_flows_massive__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_47'] = x__fetch_etf_flows_massive__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_48'] = x__fetch_etf_flows_massive__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_49'] = x__fetch_etf_flows_massive__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_50'] = x__fetch_etf_flows_massive__mutmut_50 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_51'] = x__fetch_etf_flows_massive__mutmut_51 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_52'] = x__fetch_etf_flows_massive__mutmut_52 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_53'] = x__fetch_etf_flows_massive__mutmut_53 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_54'] = x__fetch_etf_flows_massive__mutmut_54 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_55'] = x__fetch_etf_flows_massive__mutmut_55 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_56'] = x__fetch_etf_flows_massive__mutmut_56 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_57'] = x__fetch_etf_flows_massive__mutmut_57 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_58'] = x__fetch_etf_flows_massive__mutmut_58 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_59'] = x__fetch_etf_flows_massive__mutmut_59 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_60'] = x__fetch_etf_flows_massive__mutmut_60 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_61'] = x__fetch_etf_flows_massive__mutmut_61 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_62'] = x__fetch_etf_flows_massive__mutmut_62 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_63'] = x__fetch_etf_flows_massive__mutmut_63 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_64'] = x__fetch_etf_flows_massive__mutmut_64 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_65'] = x__fetch_etf_flows_massive__mutmut_65 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_66'] = x__fetch_etf_flows_massive__mutmut_66 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_67'] = x__fetch_etf_flows_massive__mutmut_67 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_68'] = x__fetch_etf_flows_massive__mutmut_68 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_69'] = x__fetch_etf_flows_massive__mutmut_69 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_70'] = x__fetch_etf_flows_massive__mutmut_70 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_71'] = x__fetch_etf_flows_massive__mutmut_71 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_72'] = x__fetch_etf_flows_massive__mutmut_72 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_73'] = x__fetch_etf_flows_massive__mutmut_73 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_74'] = x__fetch_etf_flows_massive__mutmut_74 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_75'] = x__fetch_etf_flows_massive__mutmut_75 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_76'] = x__fetch_etf_flows_massive__mutmut_76 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_77'] = x__fetch_etf_flows_massive__mutmut_77 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_78'] = x__fetch_etf_flows_massive__mutmut_78 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_79'] = x__fetch_etf_flows_massive__mutmut_79 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_80'] = x__fetch_etf_flows_massive__mutmut_80 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_81'] = x__fetch_etf_flows_massive__mutmut_81 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_82'] = x__fetch_etf_flows_massive__mutmut_82 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_83'] = x__fetch_etf_flows_massive__mutmut_83 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_84'] = x__fetch_etf_flows_massive__mutmut_84 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_85'] = x__fetch_etf_flows_massive__mutmut_85 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_86'] = x__fetch_etf_flows_massive__mutmut_86 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_massive__mutmut['x__fetch_etf_flows_massive__mutmut_87'] = x__fetch_etf_flows_massive__mutmut_87 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_etf_flows_fallback__mutmut)
async def _fetch_etf_flows_fallback(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_orig(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_1(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = None
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_2(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(None, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_3(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period=None, interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_4(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval=None)
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_5(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_6(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_7(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", )
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_8(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="XX1moXX", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_9(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1MO", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_10(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="XX1dXX")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_11(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1D")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_12(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = None
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_13(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = None
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_14(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(None)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_15(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty and len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_16(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None and df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_17(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is not None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_18(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) <= 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_19(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 7:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_20(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            break
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_21(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = None
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_22(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(None)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_23(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["XXCloseXX"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_24(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_25(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["CLOSE"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_26(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = None
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_27(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(None)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_28(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["XXVolumeXX"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_29(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_30(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["VOLUME"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_31(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = None  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_32(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes / volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_33(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = None
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_34(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:+5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_35(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-6].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_36(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) >= 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_37(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 6 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_38(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = None
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_39(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[+5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_40(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-6:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_41(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = None  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_42(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) * (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_43(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 + avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_44(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 and 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_45(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 2)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_46(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = None
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_47(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(None, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_48(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, None)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_49(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_50(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, )
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_51(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) * 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_52(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(None) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_53(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() + avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_54(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[+5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_55(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-6:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_56(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 / 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_57(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 6) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_58(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1000001, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_59(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 2)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_60(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = None
    return results


async def x__fetch_etf_flows_fallback__mutmut_61(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "XXflow_5d_mXX": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_62(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "FLOW_5D_M": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_63(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "XXflow_1d_mXX": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_64(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "FLOW_1D_M": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_65(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(None, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_66(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, None),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_67(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_68(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, ),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_69(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) * 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_70(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(None) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_71(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] + avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_72(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[+1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_73(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-2] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_74(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1000001, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_75(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 2),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_76(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "XXtrendXX": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_77(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "TREND": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_78(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "XXinflowXX" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_79(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "INFLOW" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_80(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio >= 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_81(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 1.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_82(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "XXoutflowXX" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_83(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "OUTFLOW" if flow_ratio < -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_84(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio <= -0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_85(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < +0.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_86(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -1.1 else "neutral",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_87(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "XXneutralXX",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_88(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "NEUTRAL",
            "source": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_89(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "XXsourceXX": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_90(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "SOURCE": "volume_proxy",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_91(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "XXvolume_proxyXX",
        }
    return results


async def x__fetch_etf_flows_fallback__mutmut_92(tickers: list[str]) -> dict[str, dict]:
    """
    Fallback: estimate flows from price × volume changes vs 20-day average.
    Positive deviation in volume * price = net demand proxy.
    """
    try:
        from services.market_data import get_histories_batch

        hists = await get_histories_batch(tickers, period="1mo", interval="1d")
    except Exception:
        return {}

    results: dict[str, dict] = {}
    for etf in tickers:
        df = hists.get(etf)
        if df is None or df.empty or len(df) < 6:
            continue
        closes = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m": flow_5d_m,
            "flow_1d_m": round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend": "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source": "VOLUME_PROXY",
        }
    return results

mutants_x__fetch_etf_flows_fallback__mutmut['_mutmut_orig'] = x__fetch_etf_flows_fallback__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_1'] = x__fetch_etf_flows_fallback__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_2'] = x__fetch_etf_flows_fallback__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_3'] = x__fetch_etf_flows_fallback__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_4'] = x__fetch_etf_flows_fallback__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_5'] = x__fetch_etf_flows_fallback__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_6'] = x__fetch_etf_flows_fallback__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_7'] = x__fetch_etf_flows_fallback__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_8'] = x__fetch_etf_flows_fallback__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_9'] = x__fetch_etf_flows_fallback__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_10'] = x__fetch_etf_flows_fallback__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_11'] = x__fetch_etf_flows_fallback__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_12'] = x__fetch_etf_flows_fallback__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_13'] = x__fetch_etf_flows_fallback__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_14'] = x__fetch_etf_flows_fallback__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_15'] = x__fetch_etf_flows_fallback__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_16'] = x__fetch_etf_flows_fallback__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_17'] = x__fetch_etf_flows_fallback__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_18'] = x__fetch_etf_flows_fallback__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_19'] = x__fetch_etf_flows_fallback__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_20'] = x__fetch_etf_flows_fallback__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_21'] = x__fetch_etf_flows_fallback__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_22'] = x__fetch_etf_flows_fallback__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_23'] = x__fetch_etf_flows_fallback__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_24'] = x__fetch_etf_flows_fallback__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_25'] = x__fetch_etf_flows_fallback__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_26'] = x__fetch_etf_flows_fallback__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_27'] = x__fetch_etf_flows_fallback__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_28'] = x__fetch_etf_flows_fallback__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_29'] = x__fetch_etf_flows_fallback__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_30'] = x__fetch_etf_flows_fallback__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_31'] = x__fetch_etf_flows_fallback__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_32'] = x__fetch_etf_flows_fallback__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_33'] = x__fetch_etf_flows_fallback__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_34'] = x__fetch_etf_flows_fallback__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_35'] = x__fetch_etf_flows_fallback__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_36'] = x__fetch_etf_flows_fallback__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_37'] = x__fetch_etf_flows_fallback__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_38'] = x__fetch_etf_flows_fallback__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_39'] = x__fetch_etf_flows_fallback__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_40'] = x__fetch_etf_flows_fallback__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_41'] = x__fetch_etf_flows_fallback__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_42'] = x__fetch_etf_flows_fallback__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_43'] = x__fetch_etf_flows_fallback__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_44'] = x__fetch_etf_flows_fallback__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_45'] = x__fetch_etf_flows_fallback__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_46'] = x__fetch_etf_flows_fallback__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_47'] = x__fetch_etf_flows_fallback__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_48'] = x__fetch_etf_flows_fallback__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_49'] = x__fetch_etf_flows_fallback__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_50'] = x__fetch_etf_flows_fallback__mutmut_50 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_51'] = x__fetch_etf_flows_fallback__mutmut_51 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_52'] = x__fetch_etf_flows_fallback__mutmut_52 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_53'] = x__fetch_etf_flows_fallback__mutmut_53 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_54'] = x__fetch_etf_flows_fallback__mutmut_54 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_55'] = x__fetch_etf_flows_fallback__mutmut_55 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_56'] = x__fetch_etf_flows_fallback__mutmut_56 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_57'] = x__fetch_etf_flows_fallback__mutmut_57 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_58'] = x__fetch_etf_flows_fallback__mutmut_58 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_59'] = x__fetch_etf_flows_fallback__mutmut_59 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_60'] = x__fetch_etf_flows_fallback__mutmut_60 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_61'] = x__fetch_etf_flows_fallback__mutmut_61 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_62'] = x__fetch_etf_flows_fallback__mutmut_62 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_63'] = x__fetch_etf_flows_fallback__mutmut_63 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_64'] = x__fetch_etf_flows_fallback__mutmut_64 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_65'] = x__fetch_etf_flows_fallback__mutmut_65 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_66'] = x__fetch_etf_flows_fallback__mutmut_66 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_67'] = x__fetch_etf_flows_fallback__mutmut_67 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_68'] = x__fetch_etf_flows_fallback__mutmut_68 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_69'] = x__fetch_etf_flows_fallback__mutmut_69 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_70'] = x__fetch_etf_flows_fallback__mutmut_70 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_71'] = x__fetch_etf_flows_fallback__mutmut_71 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_72'] = x__fetch_etf_flows_fallback__mutmut_72 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_73'] = x__fetch_etf_flows_fallback__mutmut_73 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_74'] = x__fetch_etf_flows_fallback__mutmut_74 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_75'] = x__fetch_etf_flows_fallback__mutmut_75 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_76'] = x__fetch_etf_flows_fallback__mutmut_76 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_77'] = x__fetch_etf_flows_fallback__mutmut_77 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_78'] = x__fetch_etf_flows_fallback__mutmut_78 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_79'] = x__fetch_etf_flows_fallback__mutmut_79 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_80'] = x__fetch_etf_flows_fallback__mutmut_80 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_81'] = x__fetch_etf_flows_fallback__mutmut_81 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_82'] = x__fetch_etf_flows_fallback__mutmut_82 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_83'] = x__fetch_etf_flows_fallback__mutmut_83 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_84'] = x__fetch_etf_flows_fallback__mutmut_84 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_85'] = x__fetch_etf_flows_fallback__mutmut_85 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_86'] = x__fetch_etf_flows_fallback__mutmut_86 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_87'] = x__fetch_etf_flows_fallback__mutmut_87 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_88'] = x__fetch_etf_flows_fallback__mutmut_88 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_89'] = x__fetch_etf_flows_fallback__mutmut_89 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_90'] = x__fetch_etf_flows_fallback__mutmut_90 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_91'] = x__fetch_etf_flows_fallback__mutmut_91 # type: ignore # mutmut generated
mutants_x__fetch_etf_flows_fallback__mutmut['x__fetch_etf_flows_fallback__mutmut_92'] = x__fetch_etf_flows_fallback__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_etf_flows__mutmut)
async def get_etf_flows() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_orig() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_1() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = None
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_2() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None or now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_3() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["XXdataXX"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_4() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["DATA"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_5() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_6() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now + _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_7() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["XXtsXX"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_8() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["TS"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_9() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] <= _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_10() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["XXdataXX"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_11() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["DATA"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_12() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = None
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_13() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(None)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_14() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_15() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info(None)
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_16() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("XX[etf_flows] Massive unavailable — using volume proxy fallbackXX")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_17() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_18() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[ETF_FLOWS] MASSIVE UNAVAILABLE — USING VOLUME PROXY FALLBACK")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_19() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = None

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_20() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(None)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_21() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = None
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_22() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["XXdataXX"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_23() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["DATA"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_24() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = None

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_25() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["XXtsXX"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_26() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["TS"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_27() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = None
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_28() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get(None) == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_29() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("XXtrendXX") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_30() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("TREND") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_31() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") != "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_32() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "XXinflowXX"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_33() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "INFLOW"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_34() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = None
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_35() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get(None) == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_36() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("XXtrendXX") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_37() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("TREND") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_38() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") != "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_39() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "XXoutflowXX"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_40() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "OUTFLOW"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


async def x_get_etf_flows__mutmut_41() -> dict:
    """Public entrypoint. Returns per-ETF flow data. 4h cache."""
    global _cache
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]

    # Try Massive first; fall back to volume proxy
    flows = await _fetch_etf_flows_massive(SECTOR_ETFS)
    if not flows:
        log.info("[etf_flows] Massive unavailable — using volume proxy fallback")
        flows = await _fetch_etf_flows_fallback(SECTOR_ETFS)

    _cache["data"] = flows
    _cache["ts"] = now

    inflow_etfs = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(None)
    return flows

mutants_x_get_etf_flows__mutmut['_mutmut_orig'] = x_get_etf_flows__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_1'] = x_get_etf_flows__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_2'] = x_get_etf_flows__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_3'] = x_get_etf_flows__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_4'] = x_get_etf_flows__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_5'] = x_get_etf_flows__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_6'] = x_get_etf_flows__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_7'] = x_get_etf_flows__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_8'] = x_get_etf_flows__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_9'] = x_get_etf_flows__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_10'] = x_get_etf_flows__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_11'] = x_get_etf_flows__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_12'] = x_get_etf_flows__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_13'] = x_get_etf_flows__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_14'] = x_get_etf_flows__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_15'] = x_get_etf_flows__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_16'] = x_get_etf_flows__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_17'] = x_get_etf_flows__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_18'] = x_get_etf_flows__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_19'] = x_get_etf_flows__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_20'] = x_get_etf_flows__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_21'] = x_get_etf_flows__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_22'] = x_get_etf_flows__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_23'] = x_get_etf_flows__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_24'] = x_get_etf_flows__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_25'] = x_get_etf_flows__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_26'] = x_get_etf_flows__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_27'] = x_get_etf_flows__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_28'] = x_get_etf_flows__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_29'] = x_get_etf_flows__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_30'] = x_get_etf_flows__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_31'] = x_get_etf_flows__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_32'] = x_get_etf_flows__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_33'] = x_get_etf_flows__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_34'] = x_get_etf_flows__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_35'] = x_get_etf_flows__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_36'] = x_get_etf_flows__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_37'] = x_get_etf_flows__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_38'] = x_get_etf_flows__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_39'] = x_get_etf_flows__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_40'] = x_get_etf_flows__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_etf_flows__mutmut['x_get_etf_flows__mutmut_41'] = x_get_etf_flows__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_flow_score_for_ticker__mutmut)
def get_flow_score_for_ticker(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_orig(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_1(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_2(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 1.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_3(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, "XXXX"

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_4(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = None
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_5(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(None)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_6(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_7(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 1.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_8(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, "XXXX"
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_9(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = None
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_10(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(None)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_11(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_12(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 1.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_13(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, "XXXX"

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_14(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = None
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_15(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get(None, 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_16(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", None)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_17(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get(0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_18(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", )
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_19(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("XXflow_5d_mXX", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_20(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("FLOW_5D_M", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_21(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 1)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_22(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(None) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_23(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) <= 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_24(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 101:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_25(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 1.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_26(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, "XXXX"
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_27(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = None
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_28(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) / (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_29(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(None, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_30(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, None) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_31(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_32(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, ) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_33(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(7.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_34(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 / 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_35(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) * 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_36(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(None) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_37(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 501 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_38(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 5) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_39(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (2 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_40(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d >= 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_41(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 1 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_42(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else +1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_43(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -2)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_44(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = None
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_45(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "XXinflowsXX" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_46(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "INFLOWS" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_47(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d >= 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_48(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 1 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_49(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "XXoutflowsXX"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_50(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "OUTFLOWS"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_51(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = None
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_52(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(None):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_53(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(None, 1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_54(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, None), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_55(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(1), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_56(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, ), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_57(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 2), reason
    except Exception:
        return 0.0, ""


def x_get_flow_score_for_ticker__mutmut_58(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 1.0, ""


def x_get_flow_score_for_ticker__mutmut_59(ticker: str, flows: dict | None) -> tuple[float, str]:
    """
    Return (score, reason) for a stock based on its sector ETF's fund flows.
    Maps ticker → sector ETF via SECTOR_MAP, then reads flow data.
    """
    if not flows:
        return 0.0, ""

    try:
        from services.sector import SECTOR_MAP

        etf = SECTOR_MAP.get(ticker)
        if not etf:
            return 0.0, ""
        flow_data = flows.get(etf)
        if not flow_data:
            return 0.0, ""

        flow_5d = flow_data.get("flow_5d_m", 0)
        # Scale: ±$500M = ±4 pts; ±$1B+ = ±6 pts (cap)
        if abs(flow_5d) < 100:
            return 0.0, ""
        pts = min(6.0, abs(flow_5d) / 500 * 4) * (1 if flow_5d > 0 else -1)
        direction = "inflows" if flow_5d > 0 else "outflows"
        reason = f"{etf} {direction} ${abs(flow_5d):.0f}M (5d)"
        return round(pts, 1), reason
    except Exception:
        return 0.0, "XXXX"

mutants_x_get_flow_score_for_ticker__mutmut['_mutmut_orig'] = x_get_flow_score_for_ticker__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_1'] = x_get_flow_score_for_ticker__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_2'] = x_get_flow_score_for_ticker__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_3'] = x_get_flow_score_for_ticker__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_4'] = x_get_flow_score_for_ticker__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_5'] = x_get_flow_score_for_ticker__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_6'] = x_get_flow_score_for_ticker__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_7'] = x_get_flow_score_for_ticker__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_8'] = x_get_flow_score_for_ticker__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_9'] = x_get_flow_score_for_ticker__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_10'] = x_get_flow_score_for_ticker__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_11'] = x_get_flow_score_for_ticker__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_12'] = x_get_flow_score_for_ticker__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_13'] = x_get_flow_score_for_ticker__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_14'] = x_get_flow_score_for_ticker__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_15'] = x_get_flow_score_for_ticker__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_16'] = x_get_flow_score_for_ticker__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_17'] = x_get_flow_score_for_ticker__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_18'] = x_get_flow_score_for_ticker__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_19'] = x_get_flow_score_for_ticker__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_20'] = x_get_flow_score_for_ticker__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_21'] = x_get_flow_score_for_ticker__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_22'] = x_get_flow_score_for_ticker__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_23'] = x_get_flow_score_for_ticker__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_24'] = x_get_flow_score_for_ticker__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_25'] = x_get_flow_score_for_ticker__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_26'] = x_get_flow_score_for_ticker__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_27'] = x_get_flow_score_for_ticker__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_28'] = x_get_flow_score_for_ticker__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_29'] = x_get_flow_score_for_ticker__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_30'] = x_get_flow_score_for_ticker__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_31'] = x_get_flow_score_for_ticker__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_32'] = x_get_flow_score_for_ticker__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_33'] = x_get_flow_score_for_ticker__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_34'] = x_get_flow_score_for_ticker__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_35'] = x_get_flow_score_for_ticker__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_36'] = x_get_flow_score_for_ticker__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_37'] = x_get_flow_score_for_ticker__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_38'] = x_get_flow_score_for_ticker__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_39'] = x_get_flow_score_for_ticker__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_40'] = x_get_flow_score_for_ticker__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_41'] = x_get_flow_score_for_ticker__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_42'] = x_get_flow_score_for_ticker__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_43'] = x_get_flow_score_for_ticker__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_44'] = x_get_flow_score_for_ticker__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_45'] = x_get_flow_score_for_ticker__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_46'] = x_get_flow_score_for_ticker__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_47'] = x_get_flow_score_for_ticker__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_48'] = x_get_flow_score_for_ticker__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_49'] = x_get_flow_score_for_ticker__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_50'] = x_get_flow_score_for_ticker__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_51'] = x_get_flow_score_for_ticker__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_52'] = x_get_flow_score_for_ticker__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_53'] = x_get_flow_score_for_ticker__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_54'] = x_get_flow_score_for_ticker__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_55'] = x_get_flow_score_for_ticker__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_56'] = x_get_flow_score_for_ticker__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_57'] = x_get_flow_score_for_ticker__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_58'] = x_get_flow_score_for_ticker__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_flow_score_for_ticker__mutmut['x_get_flow_score_for_ticker__mutmut_59'] = x_get_flow_score_for_ticker__mutmut_59 # type: ignore # mutmut generated
