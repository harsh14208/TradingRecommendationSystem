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

log = logging.getLogger("signal.trade.etf_flows")

_cache: dict = {"data": None, "ts": 0.0}
_TTL = 1800   # 30 minutes — ETF flow data via Polygon (unlimited calls)

SECTOR_ETFS = ["XLK", "XLF", "XLY", "XLC", "XLV", "XLP", "XLE", "XLI", "XLB", "XLRE", "XLU"]

_BASE = "https://api.polygon.io"


async def _fetch_etf_flows_massive(tickers: list[str]) -> dict[str, dict]:
    """Fetch ETF analytics / fund flows from Polygon.io (premium endpoint)."""
    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    import ssl, certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    results: dict[str, dict] = {}
    try:
        async with aiohttp.ClientSession() as session:
            async def fetch_one(etf: str):
                url = f"{_BASE}/partners/etf_fund_flows"
                params = {"apiKey": api_key, "ticker": etf, "limit": 10}
                try:
                    async with session.get(url, params=params, ssl=ssl_ctx,
                                           timeout=aiohttp.ClientTimeout(total=8)) as resp:
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
                            "flow_5d_m":  round(flow_5d / 1_000_000, 1),   # convert to $M
                            "flow_1d_m":  round(flow_1d / 1_000_000, 1),
                            "trend":      "inflow" if flow_5d > 0 else "outflow",
                        }
                except Exception:
                    pass

            await asyncio.gather(*[fetch_one(e) for e in tickers])
    except Exception as e:
        log.warning(f"[etf_flows] Massive fetch failed: {e}")

    return results


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
        closes  = df["Close"].astype(float)
        volumes = df["Volume"].astype(float)
        dollar_vol = closes * volumes  # daily dollar volume proxy
        avg_20 = dollar_vol.iloc[:-5].mean() if len(dollar_vol) > 5 else dollar_vol.mean()
        last_5 = dollar_vol.iloc[-5:].mean()
        flow_ratio = (last_5 - avg_20) / (avg_20 or 1)  # relative deviation
        # Approximate flow in $M from deviation in dollar volume
        flow_5d_m = round(float(dollar_vol.iloc[-5:].sum() - avg_20 * 5) / 1_000_000, 1)
        results[etf] = {
            "flow_5d_m":  flow_5d_m,
            "flow_1d_m":  round(float(dollar_vol.iloc[-1] - avg_20) / 1_000_000, 1),
            "trend":      "inflow" if flow_ratio > 0.1 else "outflow" if flow_ratio < -0.1 else "neutral",
            "source":     "volume_proxy",
        }
    return results


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
    _cache["ts"]   = now

    inflow_etfs  = [e for e, d in flows.items() if d.get("trend") == "inflow"]
    outflow_etfs = [e for e, d in flows.items() if d.get("trend") == "outflow"]
    log.info(f"[etf_flows] inflows={inflow_etfs} outflows={outflow_etfs}")
    return flows


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
