"""
Async client for Alpaca Markets REST API.
Supports both paper (PAPER_BASE) and live (LIVE_BASE) accounts.

Includes slippage protection: if the current price has moved more than
SLIPPAGE_THRESHOLD ($0.05) from the signal price within SLIPPAGE_WINDOW_MS (100ms),
the order is rejected to prevent bad fills.
"""

import ssl
import time
from typing import Any, Optional

import aiohttp
from services.http_client import get_ssl_context, shared_session

PAPER_BASE = "https://paper-api.alpaca.markets"
LIVE_BASE = "https://api.alpaca.markets"

# Slippage protection configuration
SLIPPAGE_THRESHOLD = 0.05  # $0.05 max price movement
SLIPPAGE_WINDOW_MS = 100  # 100ms lookback window


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


def _base(live: bool) -> str:
    return LIVE_BASE if live else PAPER_BASE
mutants_x__headers__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__headers__mutmut)
def _headers(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }


def x__headers__mutmut_orig(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }


def x__headers__mutmut_1(api_key: str, api_secret: str) -> dict:
    return {
        "XXAPCA-API-KEY-IDXX": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }


def x__headers__mutmut_2(api_key: str, api_secret: str) -> dict:
    return {
        "apca-api-key-id": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }


def x__headers__mutmut_3(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "XXAPCA-API-SECRET-KEYXX": api_secret,
        "Content-Type": "application/json",
    }


def x__headers__mutmut_4(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "apca-api-secret-key": api_secret,
        "Content-Type": "application/json",
    }


def x__headers__mutmut_5(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "XXContent-TypeXX": "application/json",
    }


def x__headers__mutmut_6(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "content-type": "application/json",
    }


def x__headers__mutmut_7(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "CONTENT-TYPE": "application/json",
    }


def x__headers__mutmut_8(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "XXapplication/jsonXX",
    }


def x__headers__mutmut_9(api_key: str, api_secret: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "APPLICATION/JSON",
    }

mutants_x__headers__mutmut['_mutmut_orig'] = x__headers__mutmut_orig # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_1'] = x__headers__mutmut_1 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_2'] = x__headers__mutmut_2 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_3'] = x__headers__mutmut_3 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_4'] = x__headers__mutmut_4 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_5'] = x__headers__mutmut_5 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_6'] = x__headers__mutmut_6 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_7'] = x__headers__mutmut_7 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_8'] = x__headers__mutmut_8 # type: ignore # mutmut generated
mutants_x__headers__mutmut['x__headers__mutmut_9'] = x__headers__mutmut_9 # type: ignore # mutmut generated
mutants_x__ssl_ctx__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__ssl_ctx__mutmut)
def _ssl_ctx() -> ssl.SSLContext:
    ctx = get_ssl_context()
    return ctx


def x__ssl_ctx__mutmut_orig() -> ssl.SSLContext:
    ctx = get_ssl_context()
    return ctx


def x__ssl_ctx__mutmut_1() -> ssl.SSLContext:
    ctx = None
    return ctx

mutants_x__ssl_ctx__mutmut['_mutmut_orig'] = x__ssl_ctx__mutmut_orig # type: ignore # mutmut generated
mutants_x__ssl_ctx__mutmut['x__ssl_ctx__mutmut_1'] = x__ssl_ctx__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_account__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_account__mutmut)
async def get_account(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_orig(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_1(api_key: str, api_secret: str, live: bool = True) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_2(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            None,
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_3(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_4(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, api_secret),
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_5(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_6(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_7(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, api_secret),
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_8(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(None)}/v2/account",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_9(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(None, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_10(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, None),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_11(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_account__mutmut_12(api_key: str, api_secret: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/account",
            headers=_headers(api_key, ),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_get_account__mutmut['_mutmut_orig'] = x_get_account__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_1'] = x_get_account__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_2'] = x_get_account__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_3'] = x_get_account__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_4'] = x_get_account__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_5'] = x_get_account__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_6'] = x_get_account__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_7'] = x_get_account__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_8'] = x_get_account__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_9'] = x_get_account__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_10'] = x_get_account__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_11'] = x_get_account__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_account__mutmut['x_get_account__mutmut_12'] = x_get_account__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_positions__mutmut)
async def get_positions(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_orig(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_1(api_key: str, api_secret: str, live: bool = True) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_2(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            None,
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_3(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_4(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, api_secret),
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_5(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_6(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_7(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, api_secret),
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_8(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(None)}/v2/positions",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_9(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(None, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_10(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, None),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_11(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_positions__mutmut_12(api_key: str, api_secret: str, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/positions",
            headers=_headers(api_key, ),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_get_positions__mutmut['_mutmut_orig'] = x_get_positions__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_1'] = x_get_positions__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_2'] = x_get_positions__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_3'] = x_get_positions__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_4'] = x_get_positions__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_5'] = x_get_positions__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_6'] = x_get_positions__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_7'] = x_get_positions__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_8'] = x_get_positions__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_9'] = x_get_positions__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_10'] = x_get_positions__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_11'] = x_get_positions__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_positions__mutmut['x_get_positions__mutmut_12'] = x_get_positions__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_orders__mutmut)
async def get_orders(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_orig(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_1(api_key: str, api_secret: str, status: str = "XXallXX", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_2(api_key: str, api_secret: str, status: str = "ALL", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_3(api_key: str, api_secret: str, status: str = "all", limit: int = 51, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_4(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = True) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_5(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            None,
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_6(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=None,
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_7(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_8(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_9(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_10(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_11(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_12(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_13(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(None)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_14(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(None, api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_15(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, None),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_16(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_secret),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_17(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, ),
            params={"status": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_18(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"XXstatusXX": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_19(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"STATUS": status, "limit": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_20(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "XXlimitXX": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_21(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "LIMIT": limit, "direction": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_22(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "XXdirectionXX": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_23(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "DIRECTION": "desc"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_24(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "XXdescXX"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_get_orders__mutmut_25(api_key: str, api_secret: str, status: str = "all", limit: int = 50, live: bool = False) -> list:
    async with shared_session() as s:
        async with s.get(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            params={"status": status, "limit": limit, "direction": "DESC"},
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_get_orders__mutmut['_mutmut_orig'] = x_get_orders__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_1'] = x_get_orders__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_2'] = x_get_orders__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_3'] = x_get_orders__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_4'] = x_get_orders__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_5'] = x_get_orders__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_6'] = x_get_orders__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_7'] = x_get_orders__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_8'] = x_get_orders__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_9'] = x_get_orders__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_10'] = x_get_orders__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_11'] = x_get_orders__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_12'] = x_get_orders__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_13'] = x_get_orders__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_14'] = x_get_orders__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_15'] = x_get_orders__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_16'] = x_get_orders__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_17'] = x_get_orders__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_18'] = x_get_orders__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_19'] = x_get_orders__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_20'] = x_get_orders__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_21'] = x_get_orders__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_22'] = x_get_orders__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_23'] = x_get_orders__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_24'] = x_get_orders__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_orders__mutmut['x_get_orders__mutmut_25'] = x_get_orders__mutmut_25 # type: ignore # mutmut generated


# Price history for slippage detection: {ticker: [(timestamp_ms, price), ...]}
_price_history: dict[str, list[tuple[float, float]]] = {}
mutants_x_record_price__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_record_price__mutmut)
def record_price(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_orig(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_1(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = None  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_2(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() / 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_3(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1001  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_4(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_5(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = None
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_6(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append(None)
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_7(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = None
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_8(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts + 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_9(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1001
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1000:]


def x_record_price__mutmut_10(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = None


def x_record_price__mutmut_11(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t >= cutoff][-1000:]


def x_record_price__mutmut_12(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][+1000:]


def x_record_price__mutmut_13(ticker: str, price: float):
    """Record a price tick for slippage detection."""
    ts = time.time() * 1000  # milliseconds
    if ticker not in _price_history:
        _price_history[ticker] = []
    _price_history[ticker].append((ts, price))
    # Keep only last 1000 ticks or ticks within 1 second
    cutoff = ts - 1000
    _price_history[ticker] = [(t, p) for t, p in _price_history[ticker] if t > cutoff][-1001:]

mutants_x_record_price__mutmut['_mutmut_orig'] = x_record_price__mutmut_orig # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_1'] = x_record_price__mutmut_1 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_2'] = x_record_price__mutmut_2 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_3'] = x_record_price__mutmut_3 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_4'] = x_record_price__mutmut_4 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_5'] = x_record_price__mutmut_5 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_6'] = x_record_price__mutmut_6 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_7'] = x_record_price__mutmut_7 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_8'] = x_record_price__mutmut_8 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_9'] = x_record_price__mutmut_9 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_10'] = x_record_price__mutmut_10 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_11'] = x_record_price__mutmut_11 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_12'] = x_record_price__mutmut_12 # type: ignore # mutmut generated
mutants_x_record_price__mutmut['x_record_price__mutmut_13'] = x_record_price__mutmut_13 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_check_slippage__mutmut)
def check_slippage(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_orig(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_1(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history and not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_2(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_3(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_4(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return True, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_5(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = None
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_6(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() / 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_7(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1001
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_8(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = None

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_9(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms + SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_10(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = None
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_11(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t > window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_12(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_13(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = None

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_14(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][+1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_15(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-2]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_16(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = None
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_17(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[+1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_18(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-2][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_19(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][2]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_20(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = None

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_21(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(None)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_22(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price + signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_23(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change >= SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_24(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return False, current_price  # Block the trade

    return False, current_price


def x_check_slippage__mutmut_25(ticker: str, signal_price: float) -> tuple[bool, Optional[float]]:
    """
    Check if the current price has moved more than SLIPPAGE_THRESHOLD
    from the signal price within the SLIPPAGE_WINDOW_MS window.

    Returns:
        (should_block, current_price) - should_block=True means slippage is too high
    """
    if ticker not in _price_history or not _price_history[ticker]:
        return False, None  # No price data, allow trade

    now_ms = time.time() * 1000
    window_start = now_ms - SLIPPAGE_WINDOW_MS

    # Get recent prices within the window
    recent = [(t, p) for t, p in _price_history[ticker] if t >= window_start]
    if not recent:
        # Fall back to most recent price if window is empty
        recent = [_price_history[ticker][-1]]

    current_price = recent[-1][1]
    price_change = abs(current_price - signal_price)

    if price_change > SLIPPAGE_THRESHOLD:
        return True, current_price  # Block the trade

    return True, current_price

mutants_x_check_slippage__mutmut['_mutmut_orig'] = x_check_slippage__mutmut_orig # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_1'] = x_check_slippage__mutmut_1 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_2'] = x_check_slippage__mutmut_2 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_3'] = x_check_slippage__mutmut_3 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_4'] = x_check_slippage__mutmut_4 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_5'] = x_check_slippage__mutmut_5 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_6'] = x_check_slippage__mutmut_6 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_7'] = x_check_slippage__mutmut_7 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_8'] = x_check_slippage__mutmut_8 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_9'] = x_check_slippage__mutmut_9 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_10'] = x_check_slippage__mutmut_10 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_11'] = x_check_slippage__mutmut_11 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_12'] = x_check_slippage__mutmut_12 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_13'] = x_check_slippage__mutmut_13 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_14'] = x_check_slippage__mutmut_14 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_15'] = x_check_slippage__mutmut_15 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_16'] = x_check_slippage__mutmut_16 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_17'] = x_check_slippage__mutmut_17 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_18'] = x_check_slippage__mutmut_18 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_19'] = x_check_slippage__mutmut_19 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_20'] = x_check_slippage__mutmut_20 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_21'] = x_check_slippage__mutmut_21 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_22'] = x_check_slippage__mutmut_22 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_23'] = x_check_slippage__mutmut_23 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_24'] = x_check_slippage__mutmut_24 # type: ignore # mutmut generated
mutants_x_check_slippage__mutmut['x_check_slippage__mutmut_25'] = x_check_slippage__mutmut_25 # type: ignore # mutmut generated
mutants_x_place_order__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_place_order__mutmut)
async def place_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_orig(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_1(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "XXmarketXX",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_2(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "MARKET",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_3(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "XXdayXX",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_4(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "DAY",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_5(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = True,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_6(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_7(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = None
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_8(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(None, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_9(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, None)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_10(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_11(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, )
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_12(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "XXrejectedXX": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_13(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "REJECTED": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_14(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": False,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_15(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "XXreasonXX": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_16(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "REASON": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_17(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "XXslippageXX",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_18(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "SLIPPAGE",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_19(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "XXmessageXX": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_20(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "MESSAGE": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_21(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(None):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_22(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price + signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_23(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "XXsignal_priceXX": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_24(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "SIGNAL_PRICE": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_25(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "XXcurrent_priceXX": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_26(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "CURRENT_PRICE": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_27(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "XXslippageXX": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_28(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "SLIPPAGE": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_29(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(None),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_30(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price + signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_31(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = None
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_32(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "XXsymbolXX": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_33(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "SYMBOL": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_34(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.lower(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_35(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "XXqtyXX": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_36(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "QTY": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_37(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(None),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_38(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "XXsideXX": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_39(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "SIDE": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_40(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.upper(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_41(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "XXtypeXX": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_42(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "TYPE": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_43(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "XXtime_in_forceXX": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_44(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "TIME_IN_FORCE": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_45(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" or limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_46(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type != "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_47(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "XXlimitXX" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_48(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "LIMIT" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_49(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_50(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = None
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_51(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["XXlimit_priceXX"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_52(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["LIMIT_PRICE"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_53(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(None)
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_54(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(None, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_55(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, None))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_56(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_57(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, ))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_58(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 3))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_59(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            None,
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_60(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=None,
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_61(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_62(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_63(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_64(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_65(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_66(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_67(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(None)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_68(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(None, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_69(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, None),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_70(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_order__mutmut_71(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    order_type: str = "market",
    limit_price: float | None = None,
    time_in_force: str = "day",
    signal_price: float | None = None,  # For slippage protection
    live: bool = False,
) -> dict:
    """
    Place a share-quantity order with optional slippage protection.

    Args:
        signal_price: If provided, check slippage against this price before ordering.
                     If price has moved > $0.05 within 100ms, order is rejected.
        live: If True, use the live trading endpoint instead of paper.
    """
    # Slippage check
    if signal_price is not None:
        should_block, current_price = check_slippage(symbol, signal_price)
        if should_block:
            return {
                "rejected": True,
                "reason": "slippage",
                "message": f"Price moved ${abs(current_price - signal_price):.2f} "
                f"(threshold: ${SLIPPAGE_THRESHOLD:.2f}) from signal price "
                f"${signal_price:.2f} to ${current_price:.2f}",
                "signal_price": signal_price,
                "current_price": current_price,
                "slippage": abs(current_price - signal_price),
            }

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": time_in_force,
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(round(limit_price, 2))
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, ),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_place_order__mutmut['_mutmut_orig'] = x_place_order__mutmut_orig # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_1'] = x_place_order__mutmut_1 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_2'] = x_place_order__mutmut_2 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_3'] = x_place_order__mutmut_3 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_4'] = x_place_order__mutmut_4 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_5'] = x_place_order__mutmut_5 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_6'] = x_place_order__mutmut_6 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_7'] = x_place_order__mutmut_7 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_8'] = x_place_order__mutmut_8 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_9'] = x_place_order__mutmut_9 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_10'] = x_place_order__mutmut_10 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_11'] = x_place_order__mutmut_11 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_12'] = x_place_order__mutmut_12 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_13'] = x_place_order__mutmut_13 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_14'] = x_place_order__mutmut_14 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_15'] = x_place_order__mutmut_15 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_16'] = x_place_order__mutmut_16 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_17'] = x_place_order__mutmut_17 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_18'] = x_place_order__mutmut_18 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_19'] = x_place_order__mutmut_19 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_20'] = x_place_order__mutmut_20 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_21'] = x_place_order__mutmut_21 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_22'] = x_place_order__mutmut_22 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_23'] = x_place_order__mutmut_23 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_24'] = x_place_order__mutmut_24 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_25'] = x_place_order__mutmut_25 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_26'] = x_place_order__mutmut_26 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_27'] = x_place_order__mutmut_27 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_28'] = x_place_order__mutmut_28 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_29'] = x_place_order__mutmut_29 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_30'] = x_place_order__mutmut_30 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_31'] = x_place_order__mutmut_31 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_32'] = x_place_order__mutmut_32 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_33'] = x_place_order__mutmut_33 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_34'] = x_place_order__mutmut_34 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_35'] = x_place_order__mutmut_35 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_36'] = x_place_order__mutmut_36 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_37'] = x_place_order__mutmut_37 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_38'] = x_place_order__mutmut_38 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_39'] = x_place_order__mutmut_39 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_40'] = x_place_order__mutmut_40 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_41'] = x_place_order__mutmut_41 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_42'] = x_place_order__mutmut_42 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_43'] = x_place_order__mutmut_43 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_44'] = x_place_order__mutmut_44 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_45'] = x_place_order__mutmut_45 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_46'] = x_place_order__mutmut_46 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_47'] = x_place_order__mutmut_47 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_48'] = x_place_order__mutmut_48 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_49'] = x_place_order__mutmut_49 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_50'] = x_place_order__mutmut_50 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_51'] = x_place_order__mutmut_51 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_52'] = x_place_order__mutmut_52 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_53'] = x_place_order__mutmut_53 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_54'] = x_place_order__mutmut_54 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_55'] = x_place_order__mutmut_55 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_56'] = x_place_order__mutmut_56 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_57'] = x_place_order__mutmut_57 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_58'] = x_place_order__mutmut_58 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_59'] = x_place_order__mutmut_59 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_60'] = x_place_order__mutmut_60 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_61'] = x_place_order__mutmut_61 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_62'] = x_place_order__mutmut_62 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_63'] = x_place_order__mutmut_63 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_64'] = x_place_order__mutmut_64 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_65'] = x_place_order__mutmut_65 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_66'] = x_place_order__mutmut_66 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_67'] = x_place_order__mutmut_67 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_68'] = x_place_order__mutmut_68 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_69'] = x_place_order__mutmut_69 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_70'] = x_place_order__mutmut_70 # type: ignore # mutmut generated
mutants_x_place_order__mutmut['x_place_order__mutmut_71'] = x_place_order__mutmut_71 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_place_notional_order__mutmut)
async def place_notional_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_orig(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_1(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "XXdayXX",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_2(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "DAY",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_3(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = True,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_4(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = None
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_5(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "XXsymbolXX": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_6(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "SYMBOL": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_7(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.lower(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_8(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "XXnotionalXX": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_9(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "NOTIONAL": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_10(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(None),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_11(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(None, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_12(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, None)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_13(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_14(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, )),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_15(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 3)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_16(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "XXsideXX": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_17(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "SIDE": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_18(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.upper(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_19(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "XXtypeXX": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_20(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "TYPE": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_21(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "XXmarketXX",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_22(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "MARKET",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_23(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "XXtime_in_forceXX": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_24(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "TIME_IN_FORCE": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_25(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "XXdayXX",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_26(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "DAY",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_27(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            None,
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_28(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=None,
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_29(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_30(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_31(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_32(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_33(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_34(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_35(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(None)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_36(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(None, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_37(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, None),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_38(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_notional_order__mutmut_39(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    time_in_force: str = "day",
    live: bool = False,
) -> dict:
    """
    Place a dollar-notional fractional-share market order.

    Alpaca supports fractional shares via notional ordering — the exchange
    receives a dollar amount and fills fractional shares at market price.
    Minimum notional is $1. time_in_force must be "day" for fractional orders.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",  # fractional orders require "day"
    }
    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, ),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_place_notional_order__mutmut['_mutmut_orig'] = x_place_notional_order__mutmut_orig # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_1'] = x_place_notional_order__mutmut_1 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_2'] = x_place_notional_order__mutmut_2 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_3'] = x_place_notional_order__mutmut_3 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_4'] = x_place_notional_order__mutmut_4 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_5'] = x_place_notional_order__mutmut_5 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_6'] = x_place_notional_order__mutmut_6 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_7'] = x_place_notional_order__mutmut_7 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_8'] = x_place_notional_order__mutmut_8 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_9'] = x_place_notional_order__mutmut_9 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_10'] = x_place_notional_order__mutmut_10 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_11'] = x_place_notional_order__mutmut_11 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_12'] = x_place_notional_order__mutmut_12 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_13'] = x_place_notional_order__mutmut_13 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_14'] = x_place_notional_order__mutmut_14 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_15'] = x_place_notional_order__mutmut_15 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_16'] = x_place_notional_order__mutmut_16 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_17'] = x_place_notional_order__mutmut_17 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_18'] = x_place_notional_order__mutmut_18 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_19'] = x_place_notional_order__mutmut_19 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_20'] = x_place_notional_order__mutmut_20 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_21'] = x_place_notional_order__mutmut_21 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_22'] = x_place_notional_order__mutmut_22 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_23'] = x_place_notional_order__mutmut_23 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_24'] = x_place_notional_order__mutmut_24 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_25'] = x_place_notional_order__mutmut_25 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_26'] = x_place_notional_order__mutmut_26 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_27'] = x_place_notional_order__mutmut_27 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_28'] = x_place_notional_order__mutmut_28 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_29'] = x_place_notional_order__mutmut_29 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_30'] = x_place_notional_order__mutmut_30 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_31'] = x_place_notional_order__mutmut_31 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_32'] = x_place_notional_order__mutmut_32 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_33'] = x_place_notional_order__mutmut_33 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_34'] = x_place_notional_order__mutmut_34 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_35'] = x_place_notional_order__mutmut_35 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_36'] = x_place_notional_order__mutmut_36 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_37'] = x_place_notional_order__mutmut_37 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_38'] = x_place_notional_order__mutmut_38 # type: ignore # mutmut generated
mutants_x_place_notional_order__mutmut['x_place_notional_order__mutmut_39'] = x_place_notional_order__mutmut_39 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_place_bracket_order__mutmut)
async def place_bracket_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_orig(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_1(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = True,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_2(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = None
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_3(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "XXsymbolXX": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_4(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "SYMBOL": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_5(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.lower(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_6(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "XXqtyXX": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_7(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "QTY": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_8(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(None),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_9(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(None, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_10(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, None)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_11(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_12(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, )),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_13(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 7)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_14(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "XXsideXX": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_15(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "SIDE": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_16(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.upper(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_17(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "XXtypeXX": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_18(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "TYPE": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_19(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "XXmarketXX",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_20(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "MARKET",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_21(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "XXtime_in_forceXX": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_22(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "TIME_IN_FORCE": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_23(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "XXgtcXX",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_24(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "GTC",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_25(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "XXorder_classXX": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_26(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "ORDER_CLASS": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_27(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "XXbracketXX",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_28(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "BRACKET",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_29(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "XXstop_lossXX": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_30(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "STOP_LOSS": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_31(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"XXstop_priceXX": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_32(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"STOP_PRICE": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_33(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(None)},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_34(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(None, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_35(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, None))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_36(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_37(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, ))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_38(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 3))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_39(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_40(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = None

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_41(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["XXtake_profitXX"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_42(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["TAKE_PROFIT"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_43(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"XXlimit_priceXX": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_44(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"LIMIT_PRICE": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_45(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(None)}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_46(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(None, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_47(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, None))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_48(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_49(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, ))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_50(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 3))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_51(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            None,
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_52(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=None,
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_53(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_54(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_55(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_56(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_57(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_58(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_59(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(None)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_60(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(None, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_61(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, None),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_62(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_place_bracket_order__mutmut_63(
    api_key: str,
    api_secret: str,
    symbol: str,
    qty: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    live: bool = False,
) -> dict:
    """
    Place a bracket market order with a stop-loss (and optional take-profit).

    Uses share qty (not notional) so stop/take-profit legs can be anchored
    to exact price levels from the signal's ATR stop and target.

    Alpaca supports fractional qty brackets — qty may be < 1 share.
    time_in_force must be "gtc" for bracket legs to survive past close.
    """
    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "qty": str(round(qty, 6)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, ),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_place_bracket_order__mutmut['_mutmut_orig'] = x_place_bracket_order__mutmut_orig # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_1'] = x_place_bracket_order__mutmut_1 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_2'] = x_place_bracket_order__mutmut_2 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_3'] = x_place_bracket_order__mutmut_3 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_4'] = x_place_bracket_order__mutmut_4 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_5'] = x_place_bracket_order__mutmut_5 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_6'] = x_place_bracket_order__mutmut_6 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_7'] = x_place_bracket_order__mutmut_7 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_8'] = x_place_bracket_order__mutmut_8 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_9'] = x_place_bracket_order__mutmut_9 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_10'] = x_place_bracket_order__mutmut_10 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_11'] = x_place_bracket_order__mutmut_11 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_12'] = x_place_bracket_order__mutmut_12 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_13'] = x_place_bracket_order__mutmut_13 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_14'] = x_place_bracket_order__mutmut_14 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_15'] = x_place_bracket_order__mutmut_15 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_16'] = x_place_bracket_order__mutmut_16 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_17'] = x_place_bracket_order__mutmut_17 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_18'] = x_place_bracket_order__mutmut_18 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_19'] = x_place_bracket_order__mutmut_19 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_20'] = x_place_bracket_order__mutmut_20 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_21'] = x_place_bracket_order__mutmut_21 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_22'] = x_place_bracket_order__mutmut_22 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_23'] = x_place_bracket_order__mutmut_23 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_24'] = x_place_bracket_order__mutmut_24 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_25'] = x_place_bracket_order__mutmut_25 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_26'] = x_place_bracket_order__mutmut_26 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_27'] = x_place_bracket_order__mutmut_27 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_28'] = x_place_bracket_order__mutmut_28 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_29'] = x_place_bracket_order__mutmut_29 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_30'] = x_place_bracket_order__mutmut_30 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_31'] = x_place_bracket_order__mutmut_31 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_32'] = x_place_bracket_order__mutmut_32 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_33'] = x_place_bracket_order__mutmut_33 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_34'] = x_place_bracket_order__mutmut_34 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_35'] = x_place_bracket_order__mutmut_35 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_36'] = x_place_bracket_order__mutmut_36 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_37'] = x_place_bracket_order__mutmut_37 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_38'] = x_place_bracket_order__mutmut_38 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_39'] = x_place_bracket_order__mutmut_39 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_40'] = x_place_bracket_order__mutmut_40 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_41'] = x_place_bracket_order__mutmut_41 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_42'] = x_place_bracket_order__mutmut_42 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_43'] = x_place_bracket_order__mutmut_43 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_44'] = x_place_bracket_order__mutmut_44 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_45'] = x_place_bracket_order__mutmut_45 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_46'] = x_place_bracket_order__mutmut_46 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_47'] = x_place_bracket_order__mutmut_47 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_48'] = x_place_bracket_order__mutmut_48 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_49'] = x_place_bracket_order__mutmut_49 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_50'] = x_place_bracket_order__mutmut_50 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_51'] = x_place_bracket_order__mutmut_51 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_52'] = x_place_bracket_order__mutmut_52 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_53'] = x_place_bracket_order__mutmut_53 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_54'] = x_place_bracket_order__mutmut_54 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_55'] = x_place_bracket_order__mutmut_55 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_56'] = x_place_bracket_order__mutmut_56 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_57'] = x_place_bracket_order__mutmut_57 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_58'] = x_place_bracket_order__mutmut_58 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_59'] = x_place_bracket_order__mutmut_59 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_60'] = x_place_bracket_order__mutmut_60 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_61'] = x_place_bracket_order__mutmut_61 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_62'] = x_place_bracket_order__mutmut_62 # type: ignore # mutmut generated
mutants_x_place_bracket_order__mutmut['x_place_bracket_order__mutmut_63'] = x_place_bracket_order__mutmut_63 # type: ignore # mutmut generated
mutants_x_close_position__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_close_position__mutmut)
async def close_position(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_orig(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_1(api_key: str, api_secret: str, symbol: str, live: bool = True) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_2(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            None,
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_3(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=None,
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_4(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=None,
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_5(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_6(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_7(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_8(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(None)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_9(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.lower()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_10(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(None, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_11(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, None),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_12(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_13(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, ),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_14(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status != 204:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_15(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 205:
                return {"status": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_16(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"XXstatusXX": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_17(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"STATUS": "closed"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_18(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "XXclosedXX"}
            r.raise_for_status()
            return await r.json()


async def x_close_position__mutmut_19(api_key: str, api_secret: str, symbol: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/positions/{symbol.upper()}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "CLOSED"}
            r.raise_for_status()
            return await r.json()

mutants_x_close_position__mutmut['_mutmut_orig'] = x_close_position__mutmut_orig # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_1'] = x_close_position__mutmut_1 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_2'] = x_close_position__mutmut_2 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_3'] = x_close_position__mutmut_3 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_4'] = x_close_position__mutmut_4 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_5'] = x_close_position__mutmut_5 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_6'] = x_close_position__mutmut_6 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_7'] = x_close_position__mutmut_7 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_8'] = x_close_position__mutmut_8 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_9'] = x_close_position__mutmut_9 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_10'] = x_close_position__mutmut_10 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_11'] = x_close_position__mutmut_11 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_12'] = x_close_position__mutmut_12 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_13'] = x_close_position__mutmut_13 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_14'] = x_close_position__mutmut_14 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_15'] = x_close_position__mutmut_15 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_16'] = x_close_position__mutmut_16 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_17'] = x_close_position__mutmut_17 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_18'] = x_close_position__mutmut_18 # type: ignore # mutmut generated
mutants_x_close_position__mutmut['x_close_position__mutmut_19'] = x_close_position__mutmut_19 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_cancel_order__mutmut)
async def cancel_order(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_orig(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_1(api_key: str, api_secret: str, order_id: str, live: bool = True) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_2(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            None,
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_3(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=None,
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_4(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=None,
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_5(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_6(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_7(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_8(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(None)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_9(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(None, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_10(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, None),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_11(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_12(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, ),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_13(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status != 204:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_14(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 205:
                return {"status": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_15(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"XXstatusXX": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_16(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"STATUS": "cancelled"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_17(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "XXcancelledXX"}
            r.raise_for_status()
            return await r.json()


async def x_cancel_order__mutmut_18(api_key: str, api_secret: str, order_id: str, live: bool = False) -> dict:
    async with shared_session() as s:
        async with s.delete(
            f"{_base(live)}/v2/orders/{order_id}",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            if r.status == 204:
                return {"status": "CANCELLED"}
            r.raise_for_status()
            return await r.json()

mutants_x_cancel_order__mutmut['_mutmut_orig'] = x_cancel_order__mutmut_orig # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_1'] = x_cancel_order__mutmut_1 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_2'] = x_cancel_order__mutmut_2 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_3'] = x_cancel_order__mutmut_3 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_4'] = x_cancel_order__mutmut_4 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_5'] = x_cancel_order__mutmut_5 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_6'] = x_cancel_order__mutmut_6 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_7'] = x_cancel_order__mutmut_7 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_8'] = x_cancel_order__mutmut_8 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_9'] = x_cancel_order__mutmut_9 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_10'] = x_cancel_order__mutmut_10 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_11'] = x_cancel_order__mutmut_11 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_12'] = x_cancel_order__mutmut_12 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_13'] = x_cancel_order__mutmut_13 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_14'] = x_cancel_order__mutmut_14 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_15'] = x_cancel_order__mutmut_15 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_16'] = x_cancel_order__mutmut_16 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_17'] = x_cancel_order__mutmut_17 # type: ignore # mutmut generated
mutants_x_cancel_order__mutmut['x_cancel_order__mutmut_18'] = x_cancel_order__mutmut_18 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_submit_bracket_stop_order__mutmut)
async def submit_bracket_stop_order(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_orig(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_1(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = True,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_2(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = None
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_3(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"XXtypeXX": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_4(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"TYPE": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_5(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "XXstopXX", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_6(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "STOP", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_7(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "XXstop_priceXX": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_8(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "STOP_PRICE": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_9(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(None)}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_10(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(None, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_11(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, None))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_12(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_13(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, ))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_14(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 3))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_15(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_16(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append(None)

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_17(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"XXtypeXX": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_18(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"TYPE": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_19(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "XXlimitXX", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_20(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "LIMIT", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_21(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "XXlimit_priceXX": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_22(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "LIMIT_PRICE": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_23(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(None)})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_24(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(None, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_25(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, None))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_26(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_27(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, ))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_28(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 3))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_29(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = None
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_30(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "XXsymbolXX": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_31(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "SYMBOL": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_32(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.lower(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_33(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "XXnotionalXX": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_34(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "NOTIONAL": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_35(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(None),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_36(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(None, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_37(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, None)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_38(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_39(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, )),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_40(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 3)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_41(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "XXsideXX": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_42(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "SIDE": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_43(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.upper(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_44(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "XXtypeXX": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_45(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "TYPE": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_46(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "XXmarketXX",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_47(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "MARKET",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_48(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "XXtime_in_forceXX": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_49(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "TIME_IN_FORCE": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_50(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "XXdayXX",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_51(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "DAY",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_52(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "XXorder_classXX": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_53(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "ORDER_CLASS": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_54(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "XXbracketXX" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_55(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "BRACKET" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_56(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "XXotoXX",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_57(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "OTO",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_58(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "XXstop_lossXX": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_59(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "STOP_LOSS": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_60(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"XXstop_priceXX": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_61(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"STOP_PRICE": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_62(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(None)},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_63(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(None, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_64(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, None))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_65(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_66(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, ))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_67(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 3))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_68(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_69(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = None

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_70(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["XXtake_profitXX"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_71(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["TAKE_PROFIT"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_72(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"XXlimit_priceXX": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_73(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"LIMIT_PRICE": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_74(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(None)}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_75(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(None, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_76(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, None))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_77(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_78(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, ))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_79(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 3))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_80(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            None,
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_81(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=None,
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_82(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=None,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_83(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=None,
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_84(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_85(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_86(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_87(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_88(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(None)}/v2/orders",
            headers=_headers(api_key, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_89(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(None, api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_90(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, None),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_91(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_secret),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()


async def x_submit_bracket_stop_order__mutmut_92(
    api_key: str,
    api_secret: str,
    symbol: str,
    notional: float,
    side: str,
    stop_price: float,
    take_profit_price: float | None = None,
    entry_price: float | None = None,  # unused; notional order handles sizing
    live: bool = False,
) -> dict:
    """
    Place a notional market entry order with an attached stop-loss (and optional
    take-profit) so the position is protected immediately after fill.

    Alpaca bracket orders: the parent is a market order; the stop and
    take-profit legs are submitted as OCO children and are auto-cancelled when
    either leg fills.

    Args:
        stop_price: Hard stop price (loss side). Required.
        take_profit_price: Optional target price (profit side).
        notional: Dollar amount for the entry leg (fractional shares supported).
    """
    legs: list[dict] = [{"type": "stop", "stop_price": str(round(stop_price, 2))}]
    if take_profit_price is not None:
        legs.append({"type": "limit", "limit_price": str(round(take_profit_price, 2))})

    body: dict[str, Any] = {
        "symbol": symbol.upper(),
        "notional": str(round(notional, 2)),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket" if take_profit_price else "oto",
        "stop_loss": {"stop_price": str(round(stop_price, 2))},
    }
    if take_profit_price is not None:
        body["take_profit"] = {"limit_price": str(round(take_profit_price, 2))}

    async with shared_session() as s:
        async with s.post(
            f"{_base(live)}/v2/orders",
            headers=_headers(api_key, ),
            json=body,
            ssl=_ssl_ctx(),
        ) as r:
            r.raise_for_status()
            return await r.json()

mutants_x_submit_bracket_stop_order__mutmut['_mutmut_orig'] = x_submit_bracket_stop_order__mutmut_orig # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_1'] = x_submit_bracket_stop_order__mutmut_1 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_2'] = x_submit_bracket_stop_order__mutmut_2 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_3'] = x_submit_bracket_stop_order__mutmut_3 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_4'] = x_submit_bracket_stop_order__mutmut_4 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_5'] = x_submit_bracket_stop_order__mutmut_5 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_6'] = x_submit_bracket_stop_order__mutmut_6 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_7'] = x_submit_bracket_stop_order__mutmut_7 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_8'] = x_submit_bracket_stop_order__mutmut_8 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_9'] = x_submit_bracket_stop_order__mutmut_9 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_10'] = x_submit_bracket_stop_order__mutmut_10 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_11'] = x_submit_bracket_stop_order__mutmut_11 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_12'] = x_submit_bracket_stop_order__mutmut_12 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_13'] = x_submit_bracket_stop_order__mutmut_13 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_14'] = x_submit_bracket_stop_order__mutmut_14 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_15'] = x_submit_bracket_stop_order__mutmut_15 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_16'] = x_submit_bracket_stop_order__mutmut_16 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_17'] = x_submit_bracket_stop_order__mutmut_17 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_18'] = x_submit_bracket_stop_order__mutmut_18 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_19'] = x_submit_bracket_stop_order__mutmut_19 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_20'] = x_submit_bracket_stop_order__mutmut_20 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_21'] = x_submit_bracket_stop_order__mutmut_21 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_22'] = x_submit_bracket_stop_order__mutmut_22 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_23'] = x_submit_bracket_stop_order__mutmut_23 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_24'] = x_submit_bracket_stop_order__mutmut_24 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_25'] = x_submit_bracket_stop_order__mutmut_25 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_26'] = x_submit_bracket_stop_order__mutmut_26 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_27'] = x_submit_bracket_stop_order__mutmut_27 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_28'] = x_submit_bracket_stop_order__mutmut_28 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_29'] = x_submit_bracket_stop_order__mutmut_29 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_30'] = x_submit_bracket_stop_order__mutmut_30 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_31'] = x_submit_bracket_stop_order__mutmut_31 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_32'] = x_submit_bracket_stop_order__mutmut_32 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_33'] = x_submit_bracket_stop_order__mutmut_33 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_34'] = x_submit_bracket_stop_order__mutmut_34 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_35'] = x_submit_bracket_stop_order__mutmut_35 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_36'] = x_submit_bracket_stop_order__mutmut_36 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_37'] = x_submit_bracket_stop_order__mutmut_37 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_38'] = x_submit_bracket_stop_order__mutmut_38 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_39'] = x_submit_bracket_stop_order__mutmut_39 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_40'] = x_submit_bracket_stop_order__mutmut_40 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_41'] = x_submit_bracket_stop_order__mutmut_41 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_42'] = x_submit_bracket_stop_order__mutmut_42 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_43'] = x_submit_bracket_stop_order__mutmut_43 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_44'] = x_submit_bracket_stop_order__mutmut_44 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_45'] = x_submit_bracket_stop_order__mutmut_45 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_46'] = x_submit_bracket_stop_order__mutmut_46 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_47'] = x_submit_bracket_stop_order__mutmut_47 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_48'] = x_submit_bracket_stop_order__mutmut_48 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_49'] = x_submit_bracket_stop_order__mutmut_49 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_50'] = x_submit_bracket_stop_order__mutmut_50 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_51'] = x_submit_bracket_stop_order__mutmut_51 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_52'] = x_submit_bracket_stop_order__mutmut_52 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_53'] = x_submit_bracket_stop_order__mutmut_53 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_54'] = x_submit_bracket_stop_order__mutmut_54 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_55'] = x_submit_bracket_stop_order__mutmut_55 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_56'] = x_submit_bracket_stop_order__mutmut_56 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_57'] = x_submit_bracket_stop_order__mutmut_57 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_58'] = x_submit_bracket_stop_order__mutmut_58 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_59'] = x_submit_bracket_stop_order__mutmut_59 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_60'] = x_submit_bracket_stop_order__mutmut_60 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_61'] = x_submit_bracket_stop_order__mutmut_61 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_62'] = x_submit_bracket_stop_order__mutmut_62 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_63'] = x_submit_bracket_stop_order__mutmut_63 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_64'] = x_submit_bracket_stop_order__mutmut_64 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_65'] = x_submit_bracket_stop_order__mutmut_65 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_66'] = x_submit_bracket_stop_order__mutmut_66 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_67'] = x_submit_bracket_stop_order__mutmut_67 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_68'] = x_submit_bracket_stop_order__mutmut_68 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_69'] = x_submit_bracket_stop_order__mutmut_69 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_70'] = x_submit_bracket_stop_order__mutmut_70 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_71'] = x_submit_bracket_stop_order__mutmut_71 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_72'] = x_submit_bracket_stop_order__mutmut_72 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_73'] = x_submit_bracket_stop_order__mutmut_73 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_74'] = x_submit_bracket_stop_order__mutmut_74 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_75'] = x_submit_bracket_stop_order__mutmut_75 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_76'] = x_submit_bracket_stop_order__mutmut_76 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_77'] = x_submit_bracket_stop_order__mutmut_77 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_78'] = x_submit_bracket_stop_order__mutmut_78 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_79'] = x_submit_bracket_stop_order__mutmut_79 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_80'] = x_submit_bracket_stop_order__mutmut_80 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_81'] = x_submit_bracket_stop_order__mutmut_81 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_82'] = x_submit_bracket_stop_order__mutmut_82 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_83'] = x_submit_bracket_stop_order__mutmut_83 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_84'] = x_submit_bracket_stop_order__mutmut_84 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_85'] = x_submit_bracket_stop_order__mutmut_85 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_86'] = x_submit_bracket_stop_order__mutmut_86 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_87'] = x_submit_bracket_stop_order__mutmut_87 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_88'] = x_submit_bracket_stop_order__mutmut_88 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_89'] = x_submit_bracket_stop_order__mutmut_89 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_90'] = x_submit_bracket_stop_order__mutmut_90 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_91'] = x_submit_bracket_stop_order__mutmut_91 # type: ignore # mutmut generated
mutants_x_submit_bracket_stop_order__mutmut['x_submit_bracket_stop_order__mutmut_92'] = x_submit_bracket_stop_order__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_portfolio_value__mutmut)
async def get_portfolio_value(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_orig(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_1(api_key: str, api_secret: str, live: bool = True) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_2(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = None
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_3(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(None, api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_4(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, None, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_5(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=None)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_6(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_7(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_8(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, )
    return float(account.get("equity") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_9(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(None)


async def x_get_portfolio_value__mutmut_10(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") and 0.0)


async def x_get_portfolio_value__mutmut_11(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") and account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_12(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get(None) or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_13(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("XXequityXX") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_14(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("EQUITY") or account.get("portfolio_value") or 0.0)


async def x_get_portfolio_value__mutmut_15(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get(None) or 0.0)


async def x_get_portfolio_value__mutmut_16(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("XXportfolio_valueXX") or 0.0)


async def x_get_portfolio_value__mutmut_17(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("PORTFOLIO_VALUE") or 0.0)


async def x_get_portfolio_value__mutmut_18(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return current portfolio equity (cash + unrealised P&L) in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("equity") or account.get("portfolio_value") or 1.0)

mutants_x_get_portfolio_value__mutmut['_mutmut_orig'] = x_get_portfolio_value__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_1'] = x_get_portfolio_value__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_2'] = x_get_portfolio_value__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_3'] = x_get_portfolio_value__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_4'] = x_get_portfolio_value__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_5'] = x_get_portfolio_value__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_6'] = x_get_portfolio_value__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_7'] = x_get_portfolio_value__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_8'] = x_get_portfolio_value__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_9'] = x_get_portfolio_value__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_10'] = x_get_portfolio_value__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_11'] = x_get_portfolio_value__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_12'] = x_get_portfolio_value__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_13'] = x_get_portfolio_value__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_14'] = x_get_portfolio_value__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_15'] = x_get_portfolio_value__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_16'] = x_get_portfolio_value__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_17'] = x_get_portfolio_value__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_portfolio_value__mutmut['x_get_portfolio_value__mutmut_18'] = x_get_portfolio_value__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_unrealized_pl__mutmut)
async def get_unrealized_pl(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_orig(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_1(api_key: str, api_secret: str, live: bool = True) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_2(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = None
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_3(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(None, api_secret, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_4(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, None, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_5(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=None)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_6(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_secret, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_7(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, live=live)
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_8(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, )
    return float(account.get("unrealized_pl") or 0.0)


async def x_get_unrealized_pl__mutmut_9(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(None)


async def x_get_unrealized_pl__mutmut_10(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("unrealized_pl") and 0.0)


async def x_get_unrealized_pl__mutmut_11(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get(None) or 0.0)


async def x_get_unrealized_pl__mutmut_12(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("XXunrealized_plXX") or 0.0)


async def x_get_unrealized_pl__mutmut_13(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("UNREALIZED_PL") or 0.0)


async def x_get_unrealized_pl__mutmut_14(api_key: str, api_secret: str, live: bool = False) -> float:
    """Return aggregate unrealised P&L across all open positions in dollars."""
    account = await get_account(api_key, api_secret, live=live)
    return float(account.get("unrealized_pl") or 1.0)

mutants_x_get_unrealized_pl__mutmut['_mutmut_orig'] = x_get_unrealized_pl__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_1'] = x_get_unrealized_pl__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_2'] = x_get_unrealized_pl__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_3'] = x_get_unrealized_pl__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_4'] = x_get_unrealized_pl__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_5'] = x_get_unrealized_pl__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_6'] = x_get_unrealized_pl__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_7'] = x_get_unrealized_pl__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_8'] = x_get_unrealized_pl__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_9'] = x_get_unrealized_pl__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_10'] = x_get_unrealized_pl__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_11'] = x_get_unrealized_pl__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_12'] = x_get_unrealized_pl__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_13'] = x_get_unrealized_pl__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_unrealized_pl__mutmut['x_get_unrealized_pl__mutmut_14'] = x_get_unrealized_pl__mutmut_14 # type: ignore # mutmut generated
