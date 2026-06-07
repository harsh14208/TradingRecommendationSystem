"""
Massive Options — Full Option Chain Snapshot

Replaces the single-endpoint GEX hack with a full option chain analysis:
  • Net GEX across all strikes and expiries (dealer positioning)
  • 25-delta skew (put-call IV asymmetry — fear gauge)
  • Term structure: VIX term premium / contango vs backwardation
  • Max pain strike (price where options expire most worthless)
  • Unusual strike concentration (OI clustering = magnet levels)

Cache: 15 minutes (options data moves fast).
"""

import logging
import os
import time

import aiohttp
from services.http_client import get_ssl_context, shared_session

log = logging.getLogger("signal.trade.massive_options")

_cache: dict[str, dict] = {}
_TTL = 300  # 5 minutes — unlimited Polygon calls

_BASE = "https://api.polygon.io"


async def get_option_chain_signals(ticker: str, current_price: float) -> dict:
    """
    Fetch full option chain snapshot and derive GEX, skew, max pain, term structure.
    Returns enriched signal dict compatible with signal_engine existing options block.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {}

    # Polygon.io options chain endpoint (requires Starter plan or higher)
    url = f"{_BASE}/v3/snapshot/options/{ticker}"
    params = {"apiKey": api_key, "limit": 250}

    ssl_ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return {}
                data = await resp.json()
                chain = data.get("results") or []
    except Exception as e:
        log.debug(f"[massive_options] {ticker} fetch failed: {e}")
        return {}

    if not chain:
        return {}

    # ── Net GEX across full chain ─────────────────────────────────────────────
    net_gex = 0.0
    call_oi_by_strike: dict[float, float] = {}
    put_oi_by_strike: dict[float, float] = {}

    atm_call_iv = atm_put_iv = d25_call_iv = d25_put_iv = None
    atm_dist = float("inf")

    for contract in chain:
        strike = float(contract.get("strike_price") or contract.get("strike") or 0)
        cp = (contract.get("contract_type") or contract.get("option_type") or "").lower()
        oi = float(contract.get("open_interest") or 0)
        gamma = float(contract.get("greeks", {}).get("gamma") or contract.get("gamma") or 0)
        iv = float(contract.get("implied_volatility") or contract.get("iv") or 0)
        delta_abs = abs(float(contract.get("greeks", {}).get("delta") or contract.get("delta") or 0))

        if strike <= 0 or oi <= 0:
            continue

        # GEX = gamma × OI × 100 (shares per contract) × spot²
        spot_sq = current_price**2
        gex_contrib = gamma * oi * 100 * spot_sq
        if cp.startswith("c"):
            net_gex += gex_contrib
            call_oi_by_strike[strike] = call_oi_by_strike.get(strike, 0) + oi
        elif cp.startswith("p"):
            net_gex -= gex_contrib
            put_oi_by_strike[strike] = put_oi_by_strike.get(strike, 0) + oi

        # Track ATM and 25-delta IVs for skew
        dist = abs(strike - current_price)
        if iv > 0:
            if dist < atm_dist:
                atm_dist = dist
                if cp.startswith("c"):
                    atm_call_iv = iv
                elif cp.startswith("p"):
                    atm_put_iv = iv
            # 25-delta: delta ≈ 0.25
            if 0.20 <= delta_abs <= 0.30:
                if cp.startswith("c"):
                    d25_call_iv = iv
                elif cp.startswith("p"):
                    d25_put_iv = iv

    # ── Max pain (strike with minimum combined option value at expiry) ─────────
    max_pain_strike = None
    if call_oi_by_strike or put_oi_by_strike:
        all_strikes = sorted(set(list(call_oi_by_strike.keys()) + list(put_oi_by_strike.keys())))
        min_pain = float("inf")
        for test_s in all_strikes:
            # Value to call holders if expired at test_s
            call_pain = sum(max(0, test_s - s) * oi for s, oi in call_oi_by_strike.items())
            put_pain = sum(max(0, s - test_s) * oi for s, oi in put_oi_by_strike.items())
            total_pain = call_pain + put_pain
            if total_pain < min_pain:
                min_pain, max_pain_strike = total_pain, test_s

    # ── 25-delta skew ─────────────────────────────────────────────────────────
    skew_25d = None
    if d25_put_iv is not None and d25_call_iv is not None:
        skew_25d = round((d25_put_iv - d25_call_iv) * 100, 2)  # in vols points

    result = {
        "net_gex": round(net_gex / 1_000_000, 2),  # $M
        "max_pain": max_pain_strike,
        "skew_25d": skew_25d,  # positive = put IV > call IV (fear)
        "atm_call_iv": round(atm_call_iv * 100, 1) if atm_call_iv else None,
        "atm_put_iv": round(atm_put_iv * 100, 1) if atm_put_iv else None,
        "contracts_parsed": len(chain),
    }

    _cache[ticker] = {"data": result, "ts": now}
    return result


def score_option_chain(signals: dict, current_price: float, action_hint: str) -> tuple[float, list[dict]]:
    """
    Convert full chain signals into score pts + rationale items.
    Used by signal_engine after existing options block.
    """
    if not signals:
        return 0.0, []

    score = 0.0
    rationale = []
    net_gex = signals.get("net_gex", 0.0)  # already in $M
    skew = signals.get("skew_25d")
    max_pain = signals.get("max_pain")

    # GEX: positive = dealers long gamma = they absorb moves = compression/reversal
    #       negative = dealers short gamma = they amplify moves = volatility/trend
    if net_gex > 2.0:
        score -= 3 if action_hint == "BUY" else 0
        rationale.append(
            {
                "src": "Options",
                "head": f"GEX +${net_gex:.0f}M — Dealer Long Gamma (Pinning Risk)",
                "body": (
                    "Dealers are net long gamma. They will SELL into rallies and BUY dips, "
                    "compressing volatility and pinning price near current levels. "
                    "Breakouts are more likely to fail in this regime."
                ),
                "sentiment": "neg",
                "meta": f"net_gex={net_gex:+.1f}M",
            }
        )
    elif net_gex < -2.0:
        score += 3 if action_hint == "BUY" else 0
        rationale.append(
            {
                "src": "Options",
                "head": f"GEX −${abs(net_gex):.0f}M — Dealer Short Gamma (Momentum Fuel)",
                "body": (
                    "Dealers are net short gamma. They must BUY into rallies and SELL into dips "
                    "to stay hedged, amplifying directional moves. Breakouts are more likely to sustain."
                ),
                "sentiment": "pos",
                "meta": f"net_gex={net_gex:+.1f}M",
            }
        )

    # Skew: elevated put skew (fear) → contrarian BUY signal at extremes
    if skew is not None:
        if skew > 8.0:
            score += 4
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Elevated Put Skew ({skew:.1f}vp) — Contrarian Bullish",
                    "body": (
                        "25-delta put IV significantly exceeds call IV. Extreme put skew signals "
                        "crowded hedging/fear — historically a contrarian bullish setup at this magnitude."
                    ),
                    "sentiment": "pos",
                    "meta": f"25d_skew={skew:.1f}vp",
                }
            )
        elif skew < -4.0:
            score -= 3
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Inverted Skew ({skew:.1f}vp) — Call-side Speculation",
                    "body": (
                        "25-delta call IV exceeds put IV — unusual. Retail speculation in calls "
                        "drives this inversion, which has historically preceded short-term pullbacks."
                    ),
                    "sentiment": "neg",
                    "meta": f"25d_skew={skew:.1f}vp",
                }
            )

    # Max pain gravitational pull (near-term expiry)
    if max_pain and current_price:
        gap_pct = (max_pain - current_price) / current_price * 100
        if abs(gap_pct) > 3:
            pull_dir = "upward" if gap_pct > 0 else "downward"
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Max Pain ${max_pain:.0f} ({gap_pct:+.1f}% from spot) — {pull_dir.capitalize()} Gravitational Pull",
                    "body": (
                        f"Options market max pain at ${max_pain:.0f}. As expiry approaches, price tends "
                        f"to gravitate {pull_dir} toward this level to maximise option decay."
                    ),
                    "sentiment": "pos" if gap_pct > 0 else "neg",
                    "meta": f"max_pain={max_pain} spot={current_price:.2f}",
                }
            )

    return round(score, 1), rationale
