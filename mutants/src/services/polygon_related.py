"""
Polygon.io Related Companies (v1/related-companies/{ticker}).

Returns Polygon's proprietary list of related tickers identified through
news co-occurrence and return correlation analysis. More precise than
GICS-sector grouping: NVDA's related companies include AMD, INTC, QCOM, TSM —
actual chip peers — rather than the entire XLK basket.

Used in signal_engine's Sector Peer Confirmation block:
  EXISTING: ETF-sector peers (broad — all XLK stocks)
  NEW:      Polygon related companies (narrow — actual business competitors)
  COMBINED: Both layers give higher signal quality

Cache: 24 hours per ticker (relationships are stable week-to-week).
"""

import logging
import os
import ssl
import time

import aiohttp
import certifi
from services.http_client import shared_session

log = logging.getLogger("signal.trade.polygon_related")

_cache: dict[str, dict] = {}
_TTL = 86400  # 24 hours
_BASE = "https://api.polygon.io"
_SSL_CTX = ssl.create_default_context(cafile=certifi.where())


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__get_key__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__get_key__mutmut)
def _get_key() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""


def x__get_key__mutmut_orig() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""


def x__get_key__mutmut_1() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") and ""


def x__get_key__mutmut_2() -> str:
    return os.getenv("POLYGON_API_KEY") and os.getenv("MASSIVE_API_KEY") or ""


def x__get_key__mutmut_3() -> str:
    return os.getenv(None) or os.getenv("MASSIVE_API_KEY") or ""


def x__get_key__mutmut_4() -> str:
    return os.getenv("XXPOLYGON_API_KEYXX") or os.getenv("MASSIVE_API_KEY") or ""


def x__get_key__mutmut_5() -> str:
    return os.getenv("polygon_api_key") or os.getenv("MASSIVE_API_KEY") or ""


def x__get_key__mutmut_6() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv(None) or ""


def x__get_key__mutmut_7() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("XXMASSIVE_API_KEYXX") or ""


def x__get_key__mutmut_8() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("massive_api_key") or ""


def x__get_key__mutmut_9() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or "XXXX"

mutants_x__get_key__mutmut['_mutmut_orig'] = x__get_key__mutmut_orig # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_1'] = x__get_key__mutmut_1 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_2'] = x__get_key__mutmut_2 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_3'] = x__get_key__mutmut_3 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_4'] = x__get_key__mutmut_4 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_5'] = x__get_key__mutmut_5 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_6'] = x__get_key__mutmut_6 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_7'] = x__get_key__mutmut_7 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_8'] = x__get_key__mutmut_8 # type: ignore # mutmut generated
mutants_x__get_key__mutmut['x__get_key__mutmut_9'] = x__get_key__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_related_companies__mutmut)
async def get_related_companies(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_orig(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_1(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = None
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_2(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache or now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_3(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker not in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_4(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now + _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_5(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["XXtsXX"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_6(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["TS"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_7(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] <= _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_8(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["XXtickersXX"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_9(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["TICKERS"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_10(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = None
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_11(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_12(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = None
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_13(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.lower()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_14(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = None

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_15(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"XXapiKeyXX": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_16(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apikey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_17(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"APIKEY": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_18(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(None, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_19(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=None, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_20(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=None, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_21(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=None) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_22(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_23(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_24(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_25(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, ) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_26(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=None)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_27(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=9)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_28(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_29(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 201:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_30(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = None
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_31(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"XXtickersXX": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_32(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"TICKERS": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_33(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "XXtsXX": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_34(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "TS": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_35(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = None
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_36(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = None
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_37(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") and []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_38(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get(None) or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_39(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("XXresultsXX") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_40(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("RESULTS") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_41(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = None
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_42(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get(None, "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_43(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", None) for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_44(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_45(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", ) for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_46(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("XXtickerXX", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_47(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("TICKER", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_48(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "XXXX") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_49(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get(None)]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_50(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("XXtickerXX")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_51(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("TICKER")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_52(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(None)
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_53(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = None
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_54(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"XXtickersXX": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_55(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"TICKERS": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_56(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "XXtsXX": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_57(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "TS": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_58(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = None
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_59(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"XXtickersXX": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_60(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"TICKERS": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_61(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "XXtsXX": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_62(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "TS": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:5]}")
    return tickers


async def x_get_related_companies__mutmut_63(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(None)
    return tickers


async def x_get_related_companies__mutmut_64(ticker: str) -> list[str]:
    """
    Return list of related ticker symbols for a given ticker.
    Example: NVDA → ['AMD', 'INTC', 'QCOM', 'MU', 'TSM', 'MRVL', ...]
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["tickers"]

    key = _get_key()
    if not key:
        return []

    url = f"{_BASE}/v1/related-companies/{ticker.upper()}"
    params = {"apiKey": key}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    _cache[ticker] = {"tickers": [], "ts": now}
                    return []
                data = await resp.json()
                results = data.get("results") or []
                tickers = [r.get("ticker", "") for r in results if r.get("ticker")]
    except Exception as e:
        log.debug(f"[polygon_related] {ticker}: {e}")
        _cache[ticker] = {"tickers": [], "ts": now}
        return []

    _cache[ticker] = {"tickers": tickers, "ts": now}
    log.debug(f"[polygon_related] {ticker}: {len(tickers)} related = {tickers[:6]}")
    return tickers

mutants_x_get_related_companies__mutmut['_mutmut_orig'] = x_get_related_companies__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_1'] = x_get_related_companies__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_2'] = x_get_related_companies__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_3'] = x_get_related_companies__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_4'] = x_get_related_companies__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_5'] = x_get_related_companies__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_6'] = x_get_related_companies__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_7'] = x_get_related_companies__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_8'] = x_get_related_companies__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_9'] = x_get_related_companies__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_10'] = x_get_related_companies__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_11'] = x_get_related_companies__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_12'] = x_get_related_companies__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_13'] = x_get_related_companies__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_14'] = x_get_related_companies__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_15'] = x_get_related_companies__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_16'] = x_get_related_companies__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_17'] = x_get_related_companies__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_18'] = x_get_related_companies__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_19'] = x_get_related_companies__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_20'] = x_get_related_companies__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_21'] = x_get_related_companies__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_22'] = x_get_related_companies__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_23'] = x_get_related_companies__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_24'] = x_get_related_companies__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_25'] = x_get_related_companies__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_26'] = x_get_related_companies__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_27'] = x_get_related_companies__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_28'] = x_get_related_companies__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_29'] = x_get_related_companies__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_30'] = x_get_related_companies__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_31'] = x_get_related_companies__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_32'] = x_get_related_companies__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_33'] = x_get_related_companies__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_34'] = x_get_related_companies__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_35'] = x_get_related_companies__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_36'] = x_get_related_companies__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_37'] = x_get_related_companies__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_38'] = x_get_related_companies__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_39'] = x_get_related_companies__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_40'] = x_get_related_companies__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_41'] = x_get_related_companies__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_42'] = x_get_related_companies__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_43'] = x_get_related_companies__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_44'] = x_get_related_companies__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_45'] = x_get_related_companies__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_46'] = x_get_related_companies__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_47'] = x_get_related_companies__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_48'] = x_get_related_companies__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_49'] = x_get_related_companies__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_50'] = x_get_related_companies__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_51'] = x_get_related_companies__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_52'] = x_get_related_companies__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_53'] = x_get_related_companies__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_54'] = x_get_related_companies__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_55'] = x_get_related_companies__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_56'] = x_get_related_companies__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_57'] = x_get_related_companies__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_58'] = x_get_related_companies__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_59'] = x_get_related_companies__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_60'] = x_get_related_companies__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_61'] = x_get_related_companies__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_62'] = x_get_related_companies__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_63'] = x_get_related_companies__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_related_companies__mutmut['x_get_related_companies__mutmut_64'] = x_get_related_companies__mutmut_64 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_check_related_peer_confirmation__mutmut)
async def check_related_peer_confirmation(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_orig(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_1(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_2(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("XXBUYXX", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_3(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("buy", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_4(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "XXSELLXX"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_5(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "sell"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_6(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 1.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_7(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, "XXXX"

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_8(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = None
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_9(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(None)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_10(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_11(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 1.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_12(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, "XXXX"

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_13(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = None
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_14(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t not in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_15(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) <= 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_16(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 3:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_17(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 1.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_18(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, "XXXX"  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_19(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = None
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_20(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get(None) == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_21(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("XXactionXX") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_22(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("ACTION") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_23(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") != action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_24(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = None
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_25(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(None, 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_26(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), None)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_27(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_28(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), )
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_29(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 6)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_30(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = None

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_31(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming > 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_32(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 3:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_33(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = None
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_34(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = -2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_35(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +3.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_36(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = None
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_37(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(None)}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_38(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({'XX, XX'.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_39(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:4])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_40(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 or n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_41(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming != 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_42(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 1 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_43(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked > 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_44(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 4:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_45(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = None
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_46(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = +5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_47(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -6.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_48(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = None
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_49(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(None)}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_50(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({'XX, XX'.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_51(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:4])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_52(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 1.0, ""

    return adj, reason


async def x_check_related_peer_confirmation__mutmut_53(
    ticker: str,
    action: str,
    signals_by_ticker: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if Polygon-related companies confirm a BUY/SELL signal.
    Returns (score_adjustment, rationale_string).

    Logic:
      - Fetch related companies for ticker
      - Intersect with tickers that have active signals
      - If ≥2 related peers also BUY: +2pp confidence boost
      - If 0 of ≥3 related peers are BUY: −5pp confidence penalty (stronger than ETF check)
      - No related peers in signals: 0 (neutral — don't penalise for lack of data)
    """
    if action not in ("BUY", "SELL"):
        return 0.0, ""

    related = await get_related_companies(ticker)
    if not related:
        return 0.0, ""

    # Only check related tickers that are also in our active signals
    tracked = [t for t in related if t in signals_by_ticker]
    if len(tracked) < 2:
        return 0.0, ""  # Not enough data to form a view

    confirming = [t for t in tracked if signals_by_ticker[t].get("action") == action]
    n_tracked = min(len(tracked), 5)
    n_confirming = len(confirming)

    if n_confirming >= 2:
        adj = +2.0
        reason = (
            f"Polygon related companies confirm: {n_confirming}/{n_tracked} peers "
            f"({', '.join(confirming[:3])}) also {action}. "
            f"News-correlated and return-correlated peers agreeing raises "
            f"statistical reliability of this signal."
        )
    elif n_confirming == 0 and n_tracked >= 3:
        adj = -5.0
        reason = (
            f"Polygon related companies diverge: 0/{n_tracked} peers "
            f"({', '.join(tracked[:3])}) share this {action} signal. "
            f"When business-correlated peers don't confirm, the signal is likely "
            f"stock-specific noise rather than sector-wide institutional flow."
        )
    else:
        return 0.0, "XXXX"

    return adj, reason

mutants_x_check_related_peer_confirmation__mutmut['_mutmut_orig'] = x_check_related_peer_confirmation__mutmut_orig # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_1'] = x_check_related_peer_confirmation__mutmut_1 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_2'] = x_check_related_peer_confirmation__mutmut_2 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_3'] = x_check_related_peer_confirmation__mutmut_3 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_4'] = x_check_related_peer_confirmation__mutmut_4 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_5'] = x_check_related_peer_confirmation__mutmut_5 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_6'] = x_check_related_peer_confirmation__mutmut_6 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_7'] = x_check_related_peer_confirmation__mutmut_7 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_8'] = x_check_related_peer_confirmation__mutmut_8 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_9'] = x_check_related_peer_confirmation__mutmut_9 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_10'] = x_check_related_peer_confirmation__mutmut_10 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_11'] = x_check_related_peer_confirmation__mutmut_11 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_12'] = x_check_related_peer_confirmation__mutmut_12 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_13'] = x_check_related_peer_confirmation__mutmut_13 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_14'] = x_check_related_peer_confirmation__mutmut_14 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_15'] = x_check_related_peer_confirmation__mutmut_15 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_16'] = x_check_related_peer_confirmation__mutmut_16 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_17'] = x_check_related_peer_confirmation__mutmut_17 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_18'] = x_check_related_peer_confirmation__mutmut_18 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_19'] = x_check_related_peer_confirmation__mutmut_19 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_20'] = x_check_related_peer_confirmation__mutmut_20 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_21'] = x_check_related_peer_confirmation__mutmut_21 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_22'] = x_check_related_peer_confirmation__mutmut_22 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_23'] = x_check_related_peer_confirmation__mutmut_23 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_24'] = x_check_related_peer_confirmation__mutmut_24 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_25'] = x_check_related_peer_confirmation__mutmut_25 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_26'] = x_check_related_peer_confirmation__mutmut_26 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_27'] = x_check_related_peer_confirmation__mutmut_27 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_28'] = x_check_related_peer_confirmation__mutmut_28 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_29'] = x_check_related_peer_confirmation__mutmut_29 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_30'] = x_check_related_peer_confirmation__mutmut_30 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_31'] = x_check_related_peer_confirmation__mutmut_31 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_32'] = x_check_related_peer_confirmation__mutmut_32 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_33'] = x_check_related_peer_confirmation__mutmut_33 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_34'] = x_check_related_peer_confirmation__mutmut_34 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_35'] = x_check_related_peer_confirmation__mutmut_35 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_36'] = x_check_related_peer_confirmation__mutmut_36 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_37'] = x_check_related_peer_confirmation__mutmut_37 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_38'] = x_check_related_peer_confirmation__mutmut_38 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_39'] = x_check_related_peer_confirmation__mutmut_39 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_40'] = x_check_related_peer_confirmation__mutmut_40 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_41'] = x_check_related_peer_confirmation__mutmut_41 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_42'] = x_check_related_peer_confirmation__mutmut_42 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_43'] = x_check_related_peer_confirmation__mutmut_43 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_44'] = x_check_related_peer_confirmation__mutmut_44 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_45'] = x_check_related_peer_confirmation__mutmut_45 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_46'] = x_check_related_peer_confirmation__mutmut_46 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_47'] = x_check_related_peer_confirmation__mutmut_47 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_48'] = x_check_related_peer_confirmation__mutmut_48 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_49'] = x_check_related_peer_confirmation__mutmut_49 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_50'] = x_check_related_peer_confirmation__mutmut_50 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_51'] = x_check_related_peer_confirmation__mutmut_51 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_52'] = x_check_related_peer_confirmation__mutmut_52 # type: ignore # mutmut generated
mutants_x_check_related_peer_confirmation__mutmut['x_check_related_peer_confirmation__mutmut_53'] = x_check_related_peer_confirmation__mutmut_53 # type: ignore # mutmut generated
