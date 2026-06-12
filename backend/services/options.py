"""
Options flow signals.

Data priority:
  1. Polygon Starter plan (market-implied greeks, real-time volume).
  2. CBOE delayed-quotes options chain (free, no key) — §110.
  3. yfinance fallback.

Enhanced detection across multiple expiries:
  - Cross-expiry put/call ratio
  - Sweep detection: single-strike vol >> OI (new conviction money)
  - OTM call/put spike: large directional bets on short-dated options
  - IV term structure: near-term IV spike vs back-month (event proximity)
  - Dark pool proxy: large block trades on single strike
"""

import asyncio
import json
import logging
import math
import os
import time as _time
from concurrent.futures import ThreadPoolExecutor

import yfinance as yf

from services.market_data import _retry, _session
from services.options_cboe import fetch_cboe_options_chain

log = logging.getLogger("signal.options")

# ── Redis connection (shared with market_data; same URL) ─────────────────────
# Persists IV history and options flow cache across Uvicorn workers and restarts.
# Falls back to in-process dicts if Redis is unavailable (non-critical for options).
_opt_redis = None
try:
    import redis as _redis_lib

    _opt_redis = _redis_lib.Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        socket_connect_timeout=1,
        socket_timeout=1,
        decode_responses=False,
    )
    _opt_redis.ping()
except Exception as _redis_err:
    _opt_redis = None
    log.debug("[options] Redis unavailable (%s) — using in-process IV/flow cache", _redis_err)

_IV_HIST_TTL = 366 * 86_400  # 1 year in seconds — covers full 252-day IV Rank window
_OPT_FLOW_TTL = 300  # 5 min — matches CACHE_TTL for options flow


def _bs_gamma(S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    """Black-Scholes gamma. Returns 0 on error."""
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.0
        d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
        return math.exp(-(d1**2) / 2) / (math.sqrt(2 * math.pi) * S * sigma * math.sqrt(T))
    except Exception:
        return 0.0


def _bs_vanna(S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    """
    Black-Scholes Vanna = ∂²V/∂S∂σ = −φ(d1) × d2 / σ.
    Measures how dealer delta (hedge) changes when implied volatility changes.
    Positive Vanna: dealers must buy stock if IV rises (adds upward fuel).
    Negative Vanna: dealers must sell stock if IV rises (adds downward pressure).
    Returns 0 on error.
    """
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.0
        d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        phi_d1 = math.exp(-(d1**2) / 2) / math.sqrt(2 * math.pi)
        return -phi_d1 * d2 / sigma
    except Exception:
        return 0.0


def _bs_charm(S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    """
    Black-Scholes Charm = -∂²V/∂t∂S (delta decay per day).
    Measures how dealer delta hedge changes as time decays.
    Negative Charm: dealer delta shrinks as expiry approaches; dealers sell into rallies.
    Positive Charm (OTM puts near expiry): dealers buy as put delta approaches zero.
    Returns per-day Charm (divide by 365 annualised already applied).
    """
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.0
        d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        phi = math.exp(-(d1**2) / 2) / math.sqrt(2 * math.pi)
        # Charm for a call option (per year, then divided by 365 for per-day)
        charm_annual = -phi * (2 * r * T - d2 * sigma * math.sqrt(T)) / (2 * T * sigma * math.sqrt(T))
        return charm_annual / 365.0
    except Exception:
        return 0.0


def compute_dealer_positioning(
    spot: float,
    options_chain: list[dict],
    oi_threshold: int = 100,
) -> dict:
    """
    Compute aggregate Vanna and Charm exposure across a ticker's option chain.

    Each contract: {'strike': K, 'expiry_days': T_days, 'iv': σ, 'oi': n,
                    'option_type': 'call'|'put'}

    Returns:
        net_vanna: float — positive = IV rise forces dealer buying (bullish)
        net_charm: float — negative = time decay forces dealer selling (bearish)
        vanna_signal: 'bullish'|'bearish'|'neutral'
        charm_signal: 'bullish'|'bearish'|'neutral'
        interpretation: str — human-readable summary
    """
    net_vanna = 0.0
    net_charm = 0.0

    for opt in options_chain:
        K = opt.get("strike", 0)
        T = max(opt.get("expiry_days", 0), 0.1) / 365.0
        sig = opt.get("iv", 0)
        oi = opt.get("oi", 0)
        typ = opt.get("option_type", "call")

        if K <= 0 or sig <= 0 or oi < oi_threshold:
            continue

        vanna = _bs_vanna(spot, K, T, sig)
        charm = _bs_charm(spot, K, T, sig)

        # Dealers are short calls and long puts (typical net short gamma position)
        # So dealer Vanna exposure = -call_vanna + put_vanna per unit OI
        if typ == "call":
            net_vanna -= vanna * oi
            net_charm -= charm * oi
        else:
            net_vanna += vanna * oi
            net_charm += charm * oi

    vanna_sig = "bullish" if net_vanna > 0.1 else "bearish" if net_vanna < -0.1 else "neutral"
    charm_sig = "bullish" if net_charm > 0 else "bearish" if net_charm < 0 else "neutral"

    interp_parts = []
    if vanna_sig != "neutral":
        if net_vanna > 0:
            interp_parts.append(
                f"Positive net Vanna ({net_vanna:+.2f}): if IV rises, dealers must buy "
                f"{spot:.0f} stock to re-hedge — mechanically bullish."
            )
        else:
            interp_parts.append(
                f"Negative net Vanna ({net_vanna:+.2f}): if IV rises, dealers must sell "
                f"stock — volatility spike would amplify downside."
            )
    if charm_sig != "neutral":
        if net_charm < 0:
            interp_parts.append(
                f"Negative Charm ({net_charm:+.4f}/day): delta erodes toward zero as "
                f"expiry approaches — dealers shed long delta, creating sell pressure."
            )
        else:
            interp_parts.append(
                f"Positive Charm ({net_charm:+.4f}/day): put delta decaying — dealers "
                f"unwind short delta hedges, creating buy pressure."
            )

    return {
        "net_vanna": round(net_vanna, 4),
        "net_charm": round(net_charm, 6),
        "vanna_signal": vanna_sig,
        "charm_signal": charm_sig,
        "interpretation": " ".join(interp_parts) or "Neutral dealer positioning.",
    }


_executor = ThreadPoolExecutor(max_workers=8)
CACHE_TTL = 300  # 5 min — options flow changes fast intraday

# In-process fallbacks (used when Redis is unavailable)
_opt_cache: dict[str, tuple[dict, float]] = {}
_iv_history: dict[str, list[float]] = {}
_IV_HISTORY_MAX = 252


# ── IV history helpers (Redis-persistent, in-process fallback) ───────────────


def _ivh_load(ticker: str) -> list[float]:
    """Return the stored IV history for ticker, preferring Redis over in-process."""
    local = _iv_history.get(ticker, [])
    if _opt_redis is not None:
        try:
            raw = _opt_redis.get(f"opt:ivh:{ticker}")
            if raw:
                hist = json.loads(raw)
                if len(hist) > len(local):
                    _iv_history[ticker] = hist  # warm local cache
                    return hist
        except Exception:
            pass
    return local


def _ivh_save(ticker: str, hist: list[float]) -> None:
    """Persist IV history to Redis and keep in-process cache in sync."""
    _iv_history[ticker] = hist
    if _opt_redis is not None:
        try:
            _opt_redis.setex(f"opt:ivh:{ticker}", _IV_HIST_TTL, json.dumps(hist))
        except Exception:
            pass


# ── Options flow cache helpers (Redis-persistent, in-process fallback) ───────


def _opt_cache_get(ticker: str) -> dict | None:
    """Return cached options flow dict if not expired, else None."""
    now = _time.time()
    # Check Redis first (shared across workers)
    if _opt_redis is not None:
        try:
            raw = _opt_redis.get(f"opt:flow:{ticker}")
            if raw:
                result = json.loads(raw)
                _opt_cache[ticker] = (result, now)  # warm local cache
                return result
        except Exception:
            pass
    # In-process fallback
    entry = _opt_cache.get(ticker)
    if entry and now - entry[1] < CACHE_TTL:
        return entry[0]
    return None


def _opt_cache_set(ticker: str, result: dict) -> None:
    """Store options flow dict in Redis (with TTL) and in-process cache."""
    now = _time.time()
    _opt_cache[ticker] = (result, now)
    if _opt_redis is not None:
        try:
            _opt_redis.setex(f"opt:flow:{ticker}", _OPT_FLOW_TTL, json.dumps(result))
        except Exception:
            pass


def _fetch_options_polygon(ticker: str) -> dict | None:
    """
    Fetch options chain from Polygon /v3/snapshot/options/{ticker}.
    Requires Polygon Starter plan ($30/mo). Returns None on 403 or any failure
    so the caller can fall back to yfinance.
    """
    api_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return None

    import requests

    # Paginate up to 2000 contracts (8 pages × 250) — full chain for accurate GEX.
    url = f"https://api.polygon.io/v3/snapshot/options/{ticker}"
    params = {"apiKey": api_key, "limit": 250}
    raw: list = []
    try:
        next_url: str | None = url
        pages = 0
        while next_url and pages < 8:
            if pages == 0:
                resp = requests.get(next_url, params=params, timeout=8)
            else:
                resp = requests.get(next_url, timeout=8)
            if resp.status_code == 403:
                return None  # plan gate — fall through to yfinance
            if resp.status_code != 200:
                break
            data = resp.json()
            batch = data.get("results") or []
            raw.extend(batch)
            next_url = data.get("next_url")
            pages += 1
    except Exception:
        return None

    if not raw:
        return None

    # Try underlying_asset.price / .value (populated on real-time plan; None on delayed)
    spot = None
    for r in raw:
        ua = r.get("underlying_asset", {})
        v = ua.get("price") or ua.get("value")
        if v:
            spot = float(v)
            break

    calls_pg = [r for r in raw if r.get("details", {}).get("contract_type") == "call"]
    puts_pg = [r for r in raw if r.get("details", {}).get("contract_type") == "put"]

    # Infer spot from near-ATM call delta when underlying_asset doesn't populate
    # (common on 15-min delayed Options Starter plan). Find call with delta closest
    # to 0.50 — by put-call parity that strike ≈ forward price ≈ spot.
    if spot is None and calls_pg:
        best_delta_diff = float("inf")
        for r in calls_pg:
            g = r.get("greeks") or {}
            d = g.get("delta")
            if d is not None:
                diff = abs(float(d) - 0.50)
                if diff < best_delta_diff:
                    best_delta_diff = diff
                    k = (r.get("details") or {}).get("strike_price")
                    if k:
                        spot = float(k)

    call_vol = sum(int(r.get("day", {}).get("volume", 0) or 0) for r in calls_pg)
    put_vol = sum(int(r.get("day", {}).get("volume", 0) or 0) for r in puts_pg)
    call_oi = sum(int(r.get("open_interest", 0) or 0) for r in calls_pg)
    put_oi = sum(int(r.get("open_interest", 0) or 0) for r in puts_pg)
    total_vol = call_vol + put_vol
    if total_vol < 50:
        return None

    pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None
    total_oi = call_oi + put_oi
    unusual_vol_ratio = round(total_vol / total_oi, 2) if total_oi > 0 else None

    # GEX from real market-implied gammas
    gex_total = 0.0
    if spot and spot > 0:
        for r in raw:
            greeks = r.get("greeks") or {}
            g = float(greeks.get("gamma", 0) or 0)
            oi = float(r.get("open_interest", 0) or 0)
            ctype = r.get("details", {}).get("contract_type", "call")
            if g == 0 or oi == 0:
                continue
            sign = -1 if ctype == "call" else 1
            gex_total += sign * g * oi * 100 * spot
    gex_total = round(gex_total, 0)

    # IV stats for IV Rank / term spike (group by expiry)
    from collections import defaultdict
    from datetime import datetime as _dt

    by_expiry: dict[str, list] = defaultdict(list)
    for r in raw:
        exp = (r.get("details") or {}).get("expiration_date", "")
        iv = r.get("implied_volatility")
        if exp and iv:
            by_expiry[exp].append(float(iv))

    sorted_exps = sorted(by_expiry.keys())
    near_iv = float(sum(by_expiry[sorted_exps[0]]) / len(by_expiry[sorted_exps[0]])) if sorted_exps else None
    far_iv = float(sum(by_expiry[sorted_exps[1]]) / len(by_expiry[sorted_exps[1]])) if len(sorted_exps) >= 2 else None
    iv_term_spike = round(near_iv / far_iv, 2) if near_iv and far_iv and far_iv > 0 else None

    all_ivs = [float(r["implied_volatility"]) for r in raw if r.get("implied_volatility")]
    avg_iv = round(sum(all_ivs) / len(all_ivs), 4) if all_ivs else None

    # IV Rank — load history from Redis so it survives restarts and is shared across workers
    if avg_iv and avg_iv > 0:
        hist = _ivh_load(ticker)
        hist = hist[-(_IV_HISTORY_MAX - 1) :]  # cap before append
        hist.append(avg_iv)
        _ivh_save(ticker, hist)

    iv_rank = None
    if avg_iv:
        iv_hist = _ivh_load(ticker)
        if len(iv_hist) >= 10:
            iv_low = min(iv_hist)
            iv_high = max(iv_hist)
            iv_rank = round((avg_iv - iv_low) / (iv_high - iv_low) * 100, 1) if iv_high > iv_low else 50.0

    # 25-delta skew using real deltas from Polygon greeks
    skew_25d = put_iv_25d = call_iv_25d = None
    if spot and spot > 0:
        put_25_ivs = [
            float(r.get("implied_volatility", 0))
            for r in puts_pg
            if r.get("implied_volatility") and 0.20 <= abs(float((r.get("greeks") or {}).get("delta", 0) or 0)) <= 0.30
        ]
        call_25_ivs = [
            float(r.get("implied_volatility", 0))
            for r in calls_pg
            if r.get("implied_volatility") and 0.20 <= abs(float((r.get("greeks") or {}).get("delta", 0) or 0)) <= 0.30
        ]
        if put_25_ivs and call_25_ivs:
            put_iv_25d = round(sum(put_25_ivs) / len(put_25_ivs), 4)
            call_iv_25d = round(sum(call_25_ivs) / len(call_25_ivs), 4)
            skew_25d = round(put_iv_25d - call_iv_25d, 4)

    # Sweep detection: vol >> OI
    sweep_calls, sweep_puts = [], []
    for r in raw:
        day = r.get("day") or {}
        vol = int(day.get("volume", 0) or 0)
        oi = int(r.get("open_interest", 0) or 0)
        ctype = (r.get("details") or {}).get("contract_type", "call")
        if oi > 0 and vol / oi > 5 and vol > 200:
            entry = {
                "strike": float((r.get("details") or {}).get("strike_price", 0) or 0),
                "vol": vol,
                "oi": oi,
                "vol_oi": round(vol / oi, 1),
                "iv": float(r.get("implied_volatility", 0) or 0),
                "expiry": (r.get("details") or {}).get("expiration_date", ""),
                "itm": False,
            }
            (sweep_calls if ctype == "call" else sweep_puts).append(entry)
    sweep_calls.sort(key=lambda x: -x["vol"])
    sweep_puts.sort(key=lambda x: -x["vol"])

    # OTM volumes (simple approximation — no spot means skip)
    otm_call_vol = otm_put_vol = 0
    if spot and spot > 0:
        for r in calls_pg:
            k = float((r.get("details") or {}).get("strike_price", 0) or 0)
            if k > spot:
                otm_call_vol += int((r.get("day") or {}).get("volume", 0) or 0)
        for r in puts_pg:
            k = float((r.get("details") or {}).get("strike_price", 0) or 0)
            if k < spot:
                otm_put_vol += int((r.get("day") or {}).get("volume", 0) or 0)

    # Net delta flow — Σ(delta × day_volume × 100) across all contracts.
    # Positive = net buying pressure in share-equivalents; negative = net selling.
    # Polygon real greeks make this precise (no Black-Scholes approximation needed).
    net_delta_flow = 0.0
    for r in raw:
        greeks = r.get("greeks") or {}
        d = float(greeks.get("delta", 0) or 0)
        v = float((r.get("day") or {}).get("volume", 0) or 0)
        if d != 0 and v > 0:
            net_delta_flow += d * v * 100  # share-equivalents (calls: +delta; puts: -delta)
    net_delta_flow = round(net_delta_flow, 0)
    # Normalize to a -1…+1 ratio: divide by (total_vol × 50 shares), where 50 = 0.5 ATM delta × 100
    delta_flow_ratio = round(net_delta_flow / (total_vol * 50), 3) if total_vol > 0 else 0.0

    # chains_data — top 5 OI contracts per expiry for the nearest 2 expiries.
    # Required by compute_dealer_positioning() (Vanna/Charm) in score_options().
    _today_date = _dt.utcnow().date()
    chains_data = []
    for exp_str in sorted_exps[:2]:
        try:
            exp_date = _dt.strptime(exp_str, "%Y-%m-%d").date()
            dte = max(1, (exp_date - _today_date).days)
        except Exception:
            dte = 30
        exp_calls_raw = sorted(
            [r for r in calls_pg if (r.get("details") or {}).get("expiration_date") == exp_str],
            key=lambda x: int(x.get("open_interest", 0) or 0),
            reverse=True,
        )
        exp_puts_raw = sorted(
            [r for r in puts_pg if (r.get("details") or {}).get("expiration_date") == exp_str],
            key=lambda x: int(x.get("open_interest", 0) or 0),
            reverse=True,
        )
        chains_data.append(
            {
                "dte": dte,
                "calls": [
                    {
                        "impliedVolatility": float(r.get("implied_volatility", 0) or 0),
                        "strike": float((r.get("details") or {}).get("strike_price", 0) or 0),
                        "openInterest": int(r.get("open_interest", 0) or 0),
                    }
                    for r in exp_calls_raw[:5]
                ],
                "puts": [
                    {
                        "impliedVolatility": float(r.get("implied_volatility", 0) or 0),
                        "strike": float((r.get("details") or {}).get("strike_price", 0) or 0),
                        "openInterest": int(r.get("open_interest", 0) or 0),
                    }
                    for r in exp_puts_raw[:5]
                ],
            }
        )

    # ── §70 Zero-DTE Put Activity Ratio ──────────────────────────────────────
    from datetime import datetime as _dt2

    _today_str2 = _dt2.utcnow().strftime("%Y-%m-%d")
    _zdte_put_oi = sum(
        int(r.get("open_interest", 0) or 0)
        for r in puts_pg
        if (r.get("details") or {}).get("expiration_date", "") == _today_str2
    )
    _zdte_total_put_oi = put_oi  # already computed above
    zero_dte_ratio = round(_zdte_put_oi / _zdte_total_put_oi, 3) if _zdte_total_put_oi > 0 else 0.0

    # ── §71 Max Pain ──────────────────────────────────────────────────────────
    max_pain = None
    if spot and spot > 0:
        _all_strikes = sorted(
            set(
                float((r.get("details") or {}).get("strike_price", 0) or 0)
                for r in raw
                if (r.get("details") or {}).get("strike_price")
            )
        )
        if _all_strikes and len(_all_strikes) <= 200:
            _min_pain = float("inf")
            for _s in _all_strikes:
                _pain = sum(
                    int(r.get("open_interest", 0) or 0)
                    * max(
                        0.0,
                        _s - float((r.get("details") or {}).get("strike_price", 0) or 0),
                    )
                    for r in calls_pg
                ) + sum(
                    int(r.get("open_interest", 0) or 0)
                    * max(
                        0.0,
                        float((r.get("details") or {}).get("strike_price", 0) or 0) - _s,
                    )
                    for r in puts_pg
                )
                if _pain < _min_pain:
                    _min_pain = _pain
                    max_pain = _s

    # ── §72 VRP Proxy (near_iv − far_iv term premium) ────────────────────────
    vrp_proxy = round(near_iv - far_iv, 4) if near_iv and far_iv else None

    # ── §69 GEX Flip Level ────────────────────────────────────────────────────
    gex_flip_level = None
    if spot and spot > 0:
        _strike_gex: dict[float, float] = {}
        for r in raw:
            greeks = r.get("greeks") or {}
            g = float(greeks.get("gamma", 0) or 0)
            oi = float(r.get("open_interest", 0) or 0)
            ctype = (r.get("details") or {}).get("contract_type", "call")
            k = float((r.get("details") or {}).get("strike_price", 0) or 0)
            if g == 0 or oi == 0 or k == 0:
                continue
            sign = -1 if ctype == "call" else 1
            _strike_gex[k] = _strike_gex.get(k, 0.0) + sign * g * oi * 100 * spot
        if _strike_gex:
            _sorted_ks = sorted(_strike_gex.keys())
            _cum_gex = 0.0
            _prev_k = None
            for _k in _sorted_ks:
                _prev_gex = _cum_gex
                _cum_gex += _strike_gex[_k]
                if _prev_k is not None and _prev_gex * _cum_gex < 0:
                    gex_flip_level = round((_prev_k + _k) / 2, 2)
                    break
                _prev_k = _k

    return {
        "call_vol": call_vol,
        "put_vol": put_vol,
        "pc_ratio": pc_ratio,
        "total_vol": total_vol,
        "unusual_vol_ratio": unusual_vol_ratio,
        "avg_iv": avg_iv,
        "near_iv": near_iv,
        "far_iv": far_iv,
        "iv_term_spike": iv_term_spike,
        "otm_call_vol": otm_call_vol,
        "otm_put_vol": otm_put_vol,
        "sweep_calls": sweep_calls[:3],
        "sweep_puts": sweep_puts[:3],
        "expiry": sorted_exps[0] if sorted_exps else None,
        "expiries_checked": len(sorted_exps),
        "iv_rank": iv_rank,
        "skew_25d": skew_25d,
        "put_iv_25d": put_iv_25d,
        "call_iv_25d": call_iv_25d,
        "gex": gex_total,
        "net_delta_flow": net_delta_flow,
        "delta_flow_ratio": delta_flow_ratio,
        "spot": spot,
        "chains_data": chains_data,
        "zero_dte_ratio": zero_dte_ratio,
        "max_pain": max_pain,
        "vrp_proxy": vrp_proxy,
        "gex_flip_level": gex_flip_level,
        "source": "polygon",
    }


def _fetch_options(ticker: str) -> dict:
    # Redis-backed cache shared across all Uvicorn workers — eliminates 3× duplicate fetches
    cached = _opt_cache_get(ticker)
    if cached:
        return cached

    # Try Polygon Starter plan first (real market-implied greeks + real-time volume)
    result = _fetch_options_polygon(ticker)
    if result:
        _opt_cache_set(ticker, result)
        return result

    # §110 fallback to free CBOE delayed-quotes chain before yfinance.
    result = fetch_cboe_options_chain(ticker)
    if result:
        _opt_cache_set(ticker, result)
        return result

    try:
        t = yf.Ticker(ticker, session=_session)
        expirations = _retry(lambda: t.options)
        if not expirations:
            return {}

        # Analyse first 3 expiries (catches short-dated sweep activity)
        expiries_to_check = expirations[:3]
        all_calls = []
        all_puts = []
        chains = []

        for exp in expiries_to_check:
            try:
                chain = _retry(lambda e=exp: t.option_chain(e))
                if chain and not chain.calls.empty:
                    calls_df = chain.calls.copy()
                    puts_df = chain.puts.copy()
                    calls_df["expiry"] = exp
                    puts_df["expiry"] = exp
                    all_calls.append(calls_df)
                    all_puts.append(puts_df)
                    chains.append((exp, chain.calls, chain.puts))
            except Exception as _chain_err:
                log.debug("[options] %s chain fetch for expiry %s failed: %s", ticker, exp, _chain_err)
                continue

        if not all_calls:
            return {}

        import pandas as pd

        calls = pd.concat(all_calls, ignore_index=True)
        puts = pd.concat(all_puts, ignore_index=True)

        call_vol = int(calls["volume"].fillna(0).sum())
        put_vol = int(puts["volume"].fillna(0).sum())
        call_oi = int(calls["openInterest"].fillna(0).sum())
        put_oi = int(puts["openInterest"].fillna(0).sum())
        total_vol = call_vol + put_vol

        if total_vol < 50:
            return {}

        pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None

        # ── Sweep detection: find individual strikes with vol >> OI ─────────
        sweep_calls = []
        sweep_puts = []
        for df, side in [(calls, "call"), (puts, "put")]:
            df = df[df["openInterest"].fillna(0) > 0].copy()
            df["vol_oi"] = df["volume"].fillna(0) / df["openInterest"]
            big = df[(df["vol_oi"] > 5) & (df["volume"].fillna(0) > 200)]
            for _, row in big.iterrows():
                entry = {
                    "strike": float(row.get("strike", 0)),
                    "vol": int(row.get("volume", 0)),
                    "oi": int(row.get("openInterest", 0)),
                    "vol_oi": round(float(row["vol_oi"]), 1),
                    "iv": float(row.get("impliedVolatility", 0)),
                    "expiry": row.get("expiry", ""),
                    "itm": bool(row.get("inTheMoney", False)),
                }
                if side == "call":
                    sweep_calls.append(entry)
                else:
                    sweep_puts.append(entry)

        # Top sweeps by volume
        sweep_calls.sort(key=lambda x: -x["vol"])
        sweep_puts.sort(key=lambda x: -x["vol"])

        # ── OTM activity ratio ────────────────────────────────────────────────
        otm_calls = calls[(calls["inTheMoney"].fillna(True) == False)]
        otm_puts = puts[(puts["inTheMoney"].fillna(True) == False)]
        otm_call_vol = int(otm_calls["volume"].fillna(0).sum())
        otm_put_vol = int(otm_puts["volume"].fillna(0).sum())

        # ── IV calculations ───────────────────────────────────────────────────
        near_iv = None
        far_iv = None
        if len(chains) >= 1:
            c1 = chains[0][1]  # near-term calls
            ivs = c1["impliedVolatility"].dropna()
            near_iv = float(ivs.mean()) if len(ivs) > 0 else None
        if len(chains) >= 2:
            c2 = chains[1][1]  # further calls
            ivs2 = c2["impliedVolatility"].dropna()
            far_iv = float(ivs2.mean()) if len(ivs2) > 0 else None

        # IV spike: near-term much higher than back-month signals event risk
        iv_term_spike = None
        if near_iv and far_iv and far_iv > 0:
            iv_term_spike = round(near_iv / far_iv, 2)

        # ── Gamma Exposure (GEX) ──────────────────────────────────────────────
        gex_total = 0.0
        try:
            # Use first expiry's chain for GEX (most liquid near-term)
            if chains:
                exp_str, c_df, p_df = chains[0]
                # Approximate time to expiry in years
                from datetime import datetime, timezone

                exp_dt = datetime.strptime(exp_str, "%Y-%m-%d")
                T = max((exp_dt - datetime.now(timezone.utc).replace(tzinfo=None)).days / 365.0, 1 / 365)
                spot = None
                # Fallback: use median strike as spot proxy
                if spot is None:
                    spot = float(c_df["strike"].median()) if not c_df.empty else 0
                if spot > 0:
                    for df_side, sign in [(c_df, -1), (p_df, 1)]:
                        for _, row in df_side.iterrows():
                            K = float(row.get("strike", 0))
                            oi = float(row.get("openInterest", 0) or 0)
                            iv = float(row.get("impliedVolatility", 0) or 0)
                            if K > 0 and oi > 0 and iv > 0:
                                g = _bs_gamma(spot, K, T, iv)
                                gex_total += sign * g * oi * 100 * spot
        except Exception as _gex_err:
            log.debug("[options] %s GEX calculation failed: %s", ticker, _gex_err)
        gex_total = round(gex_total, 0)

        total_oi = call_oi + put_oi
        unusual_vol_ratio = round(total_vol / total_oi, 2) if total_oi > 0 else None

        # ── Avg IV across all near-term ATM options ───────────────────────────
        try:
            atm_iv_vals = pd.concat(
                [
                    calls["impliedVolatility"].dropna().head(5),
                    puts["impliedVolatility"].dropna().head(5),
                ]
            )
            avg_iv = round(float(atm_iv_vals.mean()), 4) if len(atm_iv_vals) > 0 else None
        except Exception as _iv_err:
            log.debug("[options] %s avg IV calculation failed: %s", ticker, _iv_err)
            avg_iv = None

        # ── Track IV history for IV Rank (Redis-persistent) ──────────────
        if avg_iv and avg_iv > 0:
            hist = _ivh_load(ticker)
            hist = hist[-(_IV_HISTORY_MAX - 1) :]
            hist.append(avg_iv)
            _ivh_save(ticker, hist)

        # ── 25-delta approximation skew ───────────────────────────────────
        skew_25d = None
        put_iv_25d = None
        call_iv_25d = None
        try:
            spot = None
            # Approximate spot from ATM strike (nearest OI weighted)
            if not calls.empty and "strike" in calls.columns:
                atm_idx = (calls["strike"] - calls["strike"].median()).abs().idxmin()
                spot = float(calls.loc[atm_idx, "strike"])
            if spot and spot > 0:
                call_25 = calls[(calls["strike"] >= spot * 1.03) & (calls["strike"] <= spot * 1.10)]
                put_25 = puts[(puts["strike"] >= spot * 0.90) & (puts["strike"] <= spot * 0.97)]
                c25_iv = float(call_25["impliedVolatility"].dropna().mean()) if not call_25.empty else None
                p25_iv = float(put_25["impliedVolatility"].dropna().mean()) if not put_25.empty else None
                if c25_iv and p25_iv and c25_iv > 0:
                    skew_25d = round(p25_iv - c25_iv, 4)
                    put_iv_25d = round(p25_iv, 4)
                    call_iv_25d = round(c25_iv, 4)
        except Exception as _skew_err:
            log.debug("[options] %s skew calculation failed: %s", ticker, _skew_err)

        # ── IV Rank (uses Redis-loaded history) ───────────────────────────
        iv_rank = None
        if avg_iv:
            iv_hist = _ivh_load(ticker)
            if len(iv_hist) >= 10:
                iv_low = min(iv_hist)
                iv_high = max(iv_hist)
                iv_rank = round((avg_iv - iv_low) / (iv_high - iv_low) * 100, 1) if iv_high > iv_low else 50.0

        result = {
            "call_vol": call_vol,
            "put_vol": put_vol,
            "pc_ratio": pc_ratio,
            "total_vol": total_vol,
            "unusual_vol_ratio": unusual_vol_ratio,
            "avg_iv": avg_iv,
            "near_iv": near_iv,
            "far_iv": far_iv,
            "iv_term_spike": iv_term_spike,
            "otm_call_vol": otm_call_vol,
            "otm_put_vol": otm_put_vol,
            "sweep_calls": sweep_calls[:3],
            "sweep_puts": sweep_puts[:3],
            "expiry": expirations[0],
            "expiries_checked": len(chains),
            "iv_rank": iv_rank,
            "skew_25d": skew_25d,
            "put_iv_25d": put_iv_25d,
            "call_iv_25d": call_iv_25d,
            "gex": gex_total,
        }
        _opt_cache_set(ticker, result)
        return result

    except Exception as e:
        log.warning("[options] %s: fetch failed — %s", ticker, e)
        return {}


async def get_options_flow(ticker: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_options, ticker)


def score_options(opt: dict) -> tuple[float, list[dict]]:
    """Return (score_delta, rationale_items) from enhanced options data."""
    if not opt:
        return 0.0, []

    score = 0.0
    rationale = []
    pc = opt.get("pc_ratio")
    uv = opt.get("unusual_vol_ratio")
    iv = opt.get("avg_iv")
    call_vol = opt.get("call_vol", 0)
    put_vol = opt.get("put_vol", 0)
    sweep_calls = opt.get("sweep_calls", [])
    sweep_puts = opt.get("sweep_puts", [])
    otm_cv = opt.get("otm_call_vol", 0)
    otm_pv = opt.get("otm_put_vol", 0)
    iv_spike = opt.get("iv_term_spike")

    # ── Put/Call ratio ────────────────────────────────────────────────────────
    if pc is not None:
        if pc > 2.0:
            score += 10
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Extreme Put/Call {pc:.2f} — Contrarian Bullish",
                    "body": f"Extreme put buying (P/C = {pc:.2f}) across {opt.get('expiries_checked', 1)} expiries. "
                    f"This level of fear is historically a contrarian buy signal.",
                    "sentiment": "pos",
                    "meta": f"P/C = {pc:.2f}",
                }
            )
        elif pc > 1.4:
            score += 5
        elif pc < 0.45:
            score -= 12
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Extreme Call/Put {pc:.2f} — Contrarian Bearish",
                    "body": f"Call-side mania (P/C = {pc:.2f}) across {opt.get('expiries_checked', 1)} expiries. "
                    f"Excessive call buying often precedes reversals.",
                    "sentiment": "neg",
                    "meta": f"P/C = {pc:.2f}",
                }
            )
        elif pc < 0.65:
            score -= 6

    # ── Large call sweeps (institutional directional bet) ─────────────────────
    if sweep_calls:
        top = sweep_calls[0]
        score += min(12, top["vol_oi"] * 1.5)
        itm_label = "ITM" if top["itm"] else "OTM"
        rationale.append(
            {
                "src": "Options",
                "head": f"Large Call Sweep — ${top['strike']:.0f} {itm_label}",
                "body": f"Single-strike call sweep: {top['vol']:,} contracts traded vs {top['oi']:,} OI "
                f"({top['vol_oi']:.1f}× OI) — expiry {top['expiry']}. "
                f"IV on this strike: {top['iv'] * 100:.0f}%. "
                "Large single-strike sweeps often indicate institutional directional conviction.",
                "sentiment": "pos",
                "meta": f"Vol/OI = {top['vol_oi']:.1f}× | {top['vol']:,} contracts",
            }
        )

    # ── Large put sweeps ──────────────────────────────────────────────────────
    if sweep_puts:
        top = sweep_puts[0]
        score -= min(12, top["vol_oi"] * 1.5)
        itm_label = "ITM" if top["itm"] else "OTM"
        rationale.append(
            {
                "src": "Options",
                "head": f"Large Put Sweep — ${top['strike']:.0f} {itm_label}",
                "body": f"Single-strike put sweep: {top['vol']:,} contracts vs {top['oi']:,} OI "
                f"({top['vol_oi']:.1f}× OI) — expiry {top['expiry']}. "
                "Large put sweeps suggest protection buying or directional short bets by institutions.",
                "sentiment": "neg",
                "meta": f"Vol/OI = {top['vol_oi']:.1f}× | {top['vol']:,} contracts",
            }
        )

    # ── OTM call volume spike (speculative call buying) ───────────────────────
    if otm_cv > 0 and call_vol > 0:
        otm_call_ratio = otm_cv / call_vol
        if otm_call_ratio > 0.65 and otm_cv > 500:
            score += 6
            rationale.append(
                {
                    "src": "Options",
                    "head": f"OTM Call Buying Surge — {otm_cv:,} contracts",
                    "body": f"{otm_call_ratio * 100:.0f}% of call volume is OTM ({otm_cv:,} contracts). "
                    "Elevated OTM call activity often precedes bullish moves as traders position for upside.",
                    "sentiment": "pos",
                    "meta": f"OTM calls: {otm_cv:,} / total calls: {call_vol:,}",
                }
            )

    # ── OTM put spike (hedging activity) ─────────────────────────────────────
    if otm_pv > 0 and put_vol > 0:
        otm_put_ratio = otm_pv / put_vol
        if otm_put_ratio > 0.70 and otm_pv > 500:
            score -= 5
            rationale.append(
                {
                    "src": "Options",
                    "head": f"OTM Put Hedging Spike — {otm_pv:,} contracts",
                    "body": f"{otm_put_ratio * 100:.0f}% of put volume is OTM ({otm_pv:,} contracts). "
                    "Elevated OTM put activity suggests institutional hedging ahead of expected downside.",
                    "sentiment": "neg",
                    "meta": f"OTM puts: {otm_pv:,} / total puts: {put_vol:,}",
                }
            )

    # ── Overall unusual volume ────────────────────────────────────────────────
    if uv is not None and uv > 3.0 and not sweep_calls and not sweep_puts:
        if pc is None:
            bias = 0  # No signal when put/call data unavailable
        elif pc < 1.0:
            bias = 1  # More calls than puts = bullish
        else:
            bias = -1  # More puts than calls = bearish
        score += 6 * bias
        direction = "bullish" if bias > 0 else "bearish"
        rationale.append(
            {
                "src": "Options",
                "head": f"Unusual Options Activity — {opt.get('total_vol', 0):,} contracts",
                "body": f"Options volume is {uv:.1f}× total open interest — fresh {direction} positioning across "
                f"{opt.get('expiries_checked', 1)} expiries. Institutional money entering new positions.",
                "sentiment": "pos" if bias > 0 else "neg",
                "meta": f"Vol/OI = {uv:.1f}× | {opt.get('total_vol', 0):,} total contracts",
            }
        )

    # ── Near-term IV term structure spike ────────────────────────────────────
    # From an options-buyer view: near-term IV spike means expensive premium (bad).
    # From an equity MR view: acute near-term panic priced in = dealer hedging is
    # at its most intense right now → snap-back will be sharp once exhaustion hits.
    # Score: general -3 for event uncertainty; MR-specific +4 applied separately in
    # _assemble_signal() where we know whether the signal IS an MR BUY entry.
    if iv_spike is not None and iv_spike > 1.5:
        score -= 3  # general option-premium cost penalty
        rationale.append(
            {
                "src": "Options",
                "head": f"Near-term IV Spike ({iv_spike:.1f}× back-month) — Acute Event Pricing",
                "body": (
                    f"Short-dated IV is {iv_spike:.1f}× the next expiry's IV. "
                    "The market is pricing a large near-term move — options premium is expensive. "
                    "For directional options trades: avoid, premium is at a premium. "
                    "For equity MR entries: this acute panic level is exactly when dealer unwind "
                    "snap-backs are sharpest (see §48/§49 MR gate for the +4pp MR credit)."
                ),
                "sentiment": "neg",
                "meta": f"iv_term_spike={iv_spike:.2f} near_iv={opt.get('near_iv', 0):.3f} far_iv={opt.get('far_iv', 0):.3f}",
            }
        )

    # ── Flat IV (low IV = opportunity) ────────────────────────────────────────
    if iv is not None and iv < 0.20 and uv is not None and uv > 2:
        score += 3
        rationale.append(
            {
                "src": "Options",
                "head": f"Low IV ({iv * 100:.0f}%) with Active Volume",
                "body": f"Implied volatility is only {iv * 100:.0f}% while volume is elevated. "
                "Low IV with high activity suggests informed buying without panic premium.",
                "sentiment": "pos",
                "meta": f"IV = {iv * 100:.0f}%",
            }
        )

    elif iv is not None and iv > 0.70:
        rationale.append(
            {
                "src": "Options",
                "head": f"Very High Implied Volatility ({iv * 100:.0f}%)",
                "body": f"Options are pricing {iv * 100:.0f}% annualised vol — significantly elevated. "
                "Reduce position size; the market is pricing a large move. Premium is expensive.",
                "sentiment": "neg",
                "meta": f"Avg IV = {iv * 100:.0f}%",
            }
        )

    # ── IV Rank (expensive or cheap volatility) ───────────────────────────
    iv_rank = opt.get("iv_rank")
    skew_25d = opt.get("skew_25d")
    if iv_rank is not None:
        if iv_rank >= 80:
            rationale.append(
                {
                    "src": "Options",
                    "head": f"IV Rank {iv_rank:.0f}% — Expensive Volatility",
                    "body": f"Options are priced at the {iv_rank:.0f}th percentile of their 52-week range. "
                    "Directional plays are expensive; premium sellers have edge. Adjust position sizing down.",
                    "sentiment": "neg",
                    "meta": f"IVR = {iv_rank:.0f}%",
                }
            )
        elif iv_rank <= 20:
            score += 4
            rationale.append(
                {
                    "src": "Options",
                    "head": f"IV Rank {iv_rank:.0f}% — Cheap Volatility",
                    "body": f"Options are at the {iv_rank:.0f}th percentile of their 52-week range — historically cheap. "
                    "Long options strategies have favourable risk/reward. Good time for defined-risk trades.",
                    "sentiment": "pos",
                    "meta": f"IVR = {iv_rank:.0f}%",
                }
            )

    # ── 25-delta put/call skew ─────────────────────────────────────────────
    if skew_25d is not None:
        if skew_25d > 0.10:  # puts much more expensive than calls
            score -= 4
            rationale.append(
                {
                    "src": "Options",
                    "head": f"High Put Skew ({skew_25d * 100:.0f}pp) — Hedging Demand",
                    "body": f"25-delta puts carry {skew_25d * 100:.0f} percentage points more IV than equivalent calls. "
                    "Elevated put skew indicates institutional hedging — smart money protecting longs.",
                    "sentiment": "neg",
                    "meta": f"25d skew: +{skew_25d * 100:.0f}pp",
                }
            )
        elif skew_25d < -0.05:  # calls more expensive than puts — unusual
            score += 5
            rationale.append(
                {
                    "src": "Options",
                    "head": "Inverted Skew — Call Demand Unusual",
                    "body": f"25-delta calls carry more IV than equivalent puts ({abs(skew_25d) * 100:.0f}pp premium). "
                    "Inverted skew is rare and signals aggressive upside positioning.",
                    "sentiment": "pos",
                    "meta": f"25d skew: {skew_25d * 100:.0f}pp",
                }
            )

    # ── Gamma Exposure (GEX) ─────────────────────────────────────────────────
    gex = opt.get("gex", 0)
    if gex != 0:
        gex_b = gex / 1e9  # normalise to billions
        if gex_b > 0.5:
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Positive GEX +${gex_b:.1f}B — Price Gravity",
                    "body": (
                        "Dealers are net long gamma. As price rises they sell, as it falls they buy — "
                        "this creates gravitational pull toward high-OI strikes. Expect mean-reversion, "
                        "lower realised vol, and range-bound price action."
                    ),
                    "sentiment": "neu",
                    "meta": f"GEX = +${gex_b:.1f}B",
                }
            )
        elif gex_b < -0.5:
            score -= 3
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Negative GEX −${abs(gex_b):.1f}B — Trend Amplification",
                    "body": (
                        "Dealers are net short gamma. As price moves in any direction they must follow "
                        "— amplifying the move. Negative GEX environments see higher realised vol and "
                        "sharp directional moves. Favour momentum entries, widen stops."
                    ),
                    "sentiment": "neg",
                    "meta": f"GEX = −${abs(gex_b):.1f}B",
                }
            )

    # ── Vanna & Charm Dealer Positioning ─────────────────────────────────────
    # Build a simplified chain from the expiry data in opt dict for V/C computation.
    spot = opt.get("spot") or opt.get("price") or 0
    chains_raw = opt.get("chains_data") or []
    if spot > 0 and chains_raw:
        simple_chain = []
        for exp_data in chains_raw[:2]:  # use nearest 2 expiries for relevance
            dte = exp_data.get("dte", 30)
            calls = exp_data.get("calls") or []
            puts = exp_data.get("puts") or []
            for c in calls[:5]:  # top 5 OI strikes per expiry
                iv_ = c.get("impliedVolatility", 0) or 0
                if iv_ > 0:
                    simple_chain.append(
                        {
                            "strike": c.get("strike", spot),
                            "expiry_days": dte,
                            "iv": iv_,
                            "oi": c.get("openInterest", 0) or 0,
                            "option_type": "call",
                        }
                    )
            for p in puts[:5]:
                iv_ = p.get("impliedVolatility", 0) or 0
                if iv_ > 0:
                    simple_chain.append(
                        {
                            "strike": p.get("strike", spot),
                            "expiry_days": dte,
                            "iv": iv_,
                            "oi": p.get("openInterest", 0) or 0,
                            "option_type": "put",
                        }
                    )
        if simple_chain:
            try:
                dp = compute_dealer_positioning(spot, simple_chain)
                net_v = dp["net_vanna"]
                net_c = dp["net_charm"]
                # Score contribution: ±3 pts max based on Vanna magnitude
                if abs(net_v) > 0.5:
                    v_score = max(-3, min(3, net_v * 2))
                    score += v_score
                    if abs(v_score) >= 1.0:
                        rationale.append(
                            {
                                "src": "Options",
                                "head": f"Vanna Exposure {dp['vanna_signal'].capitalize()} ({net_v:+.2f})",
                                "body": dp["interpretation"],
                                "sentiment": "pos" if net_v > 0 else "neg",
                                "meta": f"net_vanna={net_v:+.2f} net_charm={net_c:+.4f}/day",
                            }
                        )
                # Charm: additional ±2 pts
                if abs(net_c) > 0.0001:
                    c_score = max(-2, min(2, -net_c * 5000))  # normalise to ±2 pts
                    score += c_score
                    if abs(c_score) >= 0.5:
                        rationale.append(
                            {
                                "src": "Options",
                                "head": f"Charm Flow {dp['charm_signal'].capitalize()} ({net_c:+.5f}/day)",
                                "body": (
                                    f"Time decay {'adds' if c_score > 0 else 'removes'} dealer delta "
                                    f"daily — creating structural {'buy' if c_score > 0 else 'sell'} pressure."
                                ),
                                "sentiment": "pos" if c_score > 0 else "neg",
                                "meta": f"net_charm={net_c:+.5f}/day",
                            }
                        )
            except Exception as _vanna_err:
                log.debug("[options] Vanna/Charm dealer positioning failed: %s", _vanna_err)

    # ── Net delta flow (Polygon plan only) ───────────────────────────────────
    # delta_flow_ratio = net_delta_flow / (total_vol × 50 share-eq).
    # > +0.20: more buying pressure than a neutral market would generate → bullish.
    # < -0.20: net selling pressure dominates → bearish.
    # Only available from Polygon (real greeks); yfinance path leaves this None.
    dfr = opt.get("delta_flow_ratio")
    if dfr is not None and abs(dfr) >= 0.20:
        if dfr > 0:
            score += 3
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Net Bullish Delta Flow (+{dfr:.2f} ratio)",
                    "body": (
                        f"Polygon-derived net delta flow ratio: {dfr:+.2f} — weighted buying pressure "
                        f"dominates across {opt.get('total_vol', 0):,} contracts. "
                        "Buyers are paying up for delta, not just hedging. Bullish directional signal."
                    ),
                    "sentiment": "pos",
                    "meta": f"delta_flow_ratio={dfr:+.3f} net_delta_flow={opt.get('net_delta_flow', 0):+.0f}",
                }
            )
        else:
            score -= 3
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Net Bearish Delta Flow ({dfr:.2f} ratio)",
                    "body": (
                        f"Polygon-derived net delta flow ratio: {dfr:+.2f} — weighted selling pressure "
                        f"dominates across {opt.get('total_vol', 0):,} contracts. "
                        "Institutions are net short delta; options market confirms downside pressure."
                    ),
                    "sentiment": "neg",
                    "meta": f"delta_flow_ratio={dfr:+.3f} net_delta_flow={opt.get('net_delta_flow', 0):+.0f}",
                }
            )

    # ── §70 Zero-DTE Put Spike (event risk flag) ─────────────────────────────
    _zdtr = opt.get("zero_dte_ratio", 0) or 0
    if _zdtr > 0.30:
        score -= 4
        rationale.append(
            {
                "src": "Options",
                "head": f"Zero-DTE Put Dominance — {_zdtr:.0%} of Put OI",
                "body": (
                    f"{_zdtr:.0%} of total put open interest is in zero-DTE contracts. "
                    "This signals hedging against an imminent same-day catalyst, not typical "
                    "MR panic — the move may resolve intraday rather than over 10 days."
                ),
                "sentiment": "neg",
                "meta": f"zero_dte_ratio={_zdtr:.3f}",
            }
        )

    # ── §71 Max Pain Convergence ──────────────────────────────────────────────
    _mp = opt.get("max_pain")
    _spot_mp = opt.get("spot") or opt.get("price") or 0
    _near_exp = opt.get("expiry")
    if _mp and _spot_mp and _near_exp:
        try:
            from datetime import date as _date_mp, datetime as _dt_mp

            _exp_date = _date_mp.fromisoformat(_near_exp)
            _days_to_exp = (_exp_date - _dt_mp.utcnow().date()).days
            _mp_gap_pct = (_mp - _spot_mp) / _spot_mp
            if _days_to_exp <= 2 and _mp_gap_pct > 0.02:
                score += 4
                rationale.append(
                    {
                        "src": "Options",
                        "head": f"Max Pain Pull — ${_mp:.2f} target ({_mp_gap_pct:.1%} above spot)",
                        "body": (
                            f"Options expiry in {_days_to_exp}d. Max pain level ${_mp:.2f} is "
                            f"{_mp_gap_pct:.1%} above current spot — dealer hedging creates "
                            "gravitational pull toward max pain, amplifying the MR bounce."
                        ),
                        "sentiment": "pos",
                        "meta": f"max_pain={_mp:.2f} spot={_spot_mp:.2f} dte={_days_to_exp}",
                    }
                )
        except Exception as _mp_err:
            log.debug("[options] max pain calculation failed: %s", _mp_err)

    # ── §72 VRP Proxy (IV term premium) ──────────────────────────────────────
    _vrp = opt.get("vrp_proxy")
    if _vrp is not None:
        if _vrp > 0.05:
            score += 3
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Positive Volatility Risk Premium (+{_vrp:.2f})",
                    "body": (
                        f"Near-term IV exceeds back-month IV by {_vrp:.2f} — the options market "
                        "is overcharging for near-term protection. This systematic fear overpricing "
                        "historically precedes faster bounce completions."
                    ),
                    "sentiment": "pos",
                    "meta": f"vrp_proxy={_vrp:+.4f} near_iv={opt.get('near_iv')} far_iv={opt.get('far_iv')}",
                }
            )
        elif _vrp < -0.05:
            score -= 2
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Negative VRP ({_vrp:.2f}) — Back-Month Fear",
                    "body": (
                        "Back-month IV exceeds near-term IV — longer-duration fear dominates. "
                        "Typically signals persistent structural concern rather than acute panic."
                    ),
                    "sentiment": "neg",
                    "meta": f"vrp_proxy={_vrp:+.4f}",
                }
            )

    # ── §69 GEX Flip Level Proximity ─────────────────────────────────────────
    _gfl = opt.get("gex_flip_level")
    _spot_gfl = opt.get("spot") or opt.get("price") or 0
    if _gfl and _spot_gfl and _spot_gfl > 0:
        _gfl_gap = (_gfl - _spot_gfl) / _spot_gfl
        if -0.02 <= _gfl_gap <= 0.01:
            score += 5
            rationale.append(
                {
                    "src": "Options",
                    "head": f"GEX Flip Level Proximity — ${_gfl:.2f} ({_gfl_gap:+.1%})",
                    "body": (
                        f"Price within 2% of GEX flip level ${_gfl:.2f}. Below the flip, "
                        "dealers are short gamma → they must buy as price falls, mechanically "
                        "amplifying the MR bounce. SpotGamma: 73% of bottoms occur within "
                        "0.5% of the GEX flip."
                    ),
                    "sentiment": "pos",
                    "meta": f"gex_flip={_gfl:.2f} spot={_spot_gfl:.2f} gap={_gfl_gap:+.2%}",
                }
            )
        elif _gfl_gap > 0.03:
            score -= 2
            rationale.append(
                {
                    "src": "Options",
                    "head": f"Above GEX Flip — Dealer Short Delta Zone ({_gfl_gap:+.1%})",
                    "body": "Price above flip level — dealers long gamma, dampen moves. Lower bounce energy.",
                    "sentiment": "neg",
                    "meta": f"gex_flip={_gfl:.2f} spot={_spot_gfl:.2f}",
                }
            )

    return round(score, 1), rationale
