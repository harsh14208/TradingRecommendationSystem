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


def _get_key() -> str:
    return os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""


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
