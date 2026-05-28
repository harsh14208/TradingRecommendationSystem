"""
Massive Partners — Analyst Intelligence

Three endpoints merged into one service:
  1. Bulls Bears Say    — structured bull/bear thesis per ticker
  2. Analyst Ratings   — consensus + price target from historical ratings
  3. Corporate Guidance — EPS/revenue guidance raise/cut signals

Signal scoring:
  Bulls Bears Say:
    bull_count > bear_count → +3 pts (max +6 if ratio ≥ 3:1)
    bear_count > bull_count → −3 pts (max −6)
  Analyst Ratings (consensus):
    Strong Buy consensus  → +6 pts
    Buy consensus         → +4 pts
    Hold consensus        → 0 pts
    Sell / Strong Sell    → −4 / −6 pts
  Corporate Guidance:
    EPS guidance raise    → +8 pts (strong catalyst)
    EPS guidance cut      → −10 pts
    Revenue guidance flat → 0 pts

Per-ticker cache: 6 hours (quarterly fundamentals don't move faster).
"""

import asyncio
import logging
import os
import time

import aiohttp

log = logging.getLogger("signal.trade.massive_analyst")

_cache: dict[str, dict] = {}
_TTL = 3600  # 1 hour — analyst sentiment can shift intraday on news

_BASE = "https://api.polygon.io"

import ssl as _ssl

import certifi as _certifi

_SSL_CTX = _ssl.create_default_context(cafile=_certifi.where())


async def _fetch(session: aiohttp.ClientSession, endpoint: str, params: dict) -> dict:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:
                return {}
            data = await resp.json()
            results = data.get("results") or []
            return results[0] if results else {}
    except Exception:
        return {}


async def _fetch_list(session: aiohttp.ClientSession, endpoint: str, params: dict) -> list:
    try:
        async with session.get(
            f"{_BASE}/{endpoint}", params=params, ssl=_SSL_CTX, timeout=aiohttp.ClientTimeout(total=8)
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("results") or []
    except Exception:
        return []


async def get_analyst_intelligence(ticker: str) -> dict:
    """
    Fetch Bulls Bears Say, consensus ratings, and corporate guidance for a ticker.
    Returns a unified dict used by signal_engine.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    base_params = {"apiKey": api_key, "ticker": ticker}

    async with aiohttp.ClientSession() as session:
        bulls_bears, consensus, guidance, ratings = await asyncio.gather(
            _fetch(session, "partners/bulls_bears_say", {**base_params, "limit": 1}),
            _fetch(session, "partners/consensus_ratings", base_params),
            _fetch_list(session, "partners/corporate_guidance", {**base_params, "limit": 3}),
            _fetch_list(session, "partners/analyst_ratings", {**base_params, "limit": 10}),
            return_exceptions=True,
        )

    # Make sure exceptions become empty results
    if isinstance(bulls_bears, Exception):
        bulls_bears = {}
    if isinstance(consensus, Exception):
        consensus = {}
    if isinstance(guidance, Exception):
        guidance = []
    if isinstance(ratings, Exception):
        ratings = []

    # ── Parse Bulls Bears Say ─────────────────────────────────────────────────
    bull_pts = float(bulls_bears.get("bull_count") or bulls_bears.get("bulls") or 0)
    bear_pts = float(bulls_bears.get("bear_count") or bulls_bears.get("bears") or 0)
    bull_text = bulls_bears.get("bull_summary") or bulls_bears.get("bull_case") or ""
    bear_text = bulls_bears.get("bear_summary") or bulls_bears.get("bear_case") or ""

    ratio = (bull_pts / bear_pts) if bear_pts > 0 else (bull_pts if bull_pts > 0 else 1)
    if bull_pts > bear_pts:
        bbs_score = min(6.0, 3.0 + (ratio - 1) * 0.5)
        bbs_label = "bullish"
    elif bear_pts > bull_pts:
        inv_ratio = (bear_pts / bull_pts) if bull_pts > 0 else bear_pts
        bbs_score = -min(6.0, 3.0 + (inv_ratio - 1) * 0.5)
        bbs_label = "bearish"
    else:
        bbs_score, bbs_label = 0.0, "neutral"

    # ── Parse Consensus Ratings ───────────────────────────────────────────────
    cons_key = (consensus.get("consensus") or consensus.get("recommendation") or "hold").lower()
    cons_pt = consensus.get("target_price_average") or consensus.get("target_mean")
    cons_count = int(consensus.get("analyst_count") or consensus.get("num_analysts") or 0)
    cons_score_map = {
        "strong_buy": 6,
        "buy": 4,
        "overweight": 3,
        "hold": 0,
        "underweight": -3,
        "sell": -4,
        "strong_sell": -6,
    }
    cons_score = float(cons_score_map.get(cons_key, 0))

    # ── Parse Corporate Guidance ──────────────────────────────────────────────
    guidance_score = 0.0
    guidance_summary = ""
    for g in guidance if isinstance(guidance, list) else []:
        eps_direction = (g.get("eps_direction") or g.get("eps_change") or "").lower()
        rev_direction = (g.get("revenue_direction") or g.get("revenue_change") or "").lower()
        if "raise" in eps_direction or "above" in eps_direction or "beat" in eps_direction:
            guidance_score += 8.0
            guidance_summary = f"EPS guidance raised: {g.get('eps_estimate', '')}"
            break
        elif "cut" in eps_direction or "below" in eps_direction or "miss" in eps_direction:
            guidance_score -= 10.0
            guidance_summary = f"EPS guidance cut: {g.get('eps_estimate', '')}"
            break

    result = {
        "bulls_bears": {
            "score": round(bbs_score, 1),
            "label": bbs_label,
            "bull_text": bull_text[:300],
            "bear_text": bear_text[:300],
            "bull_count": int(bull_pts),
            "bear_count": int(bear_pts),
        },
        "consensus": {
            "score": round(cons_score, 1),
            "key": cons_key,
            "target_price": float(cons_pt) if cons_pt else None,
            "analyst_count": cons_count,
        },
        "guidance": {
            "score": round(guidance_score, 1),
            "summary": guidance_summary,
        },
        "total_score": round(bbs_score + cons_score + guidance_score, 1),
    }

    _cache[ticker] = {"data": result, "ts": now}
    return result
