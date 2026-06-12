"""§110 — Free CBOE delayed-quotes options chain fetcher.

Endpoint: https://cdn.cboe.com/api/global/delayed_quotes/options/{TICKER}.json
No API key required. Provides per-contract bid/ask, IV, OI, volume, and greeks.
Used as a fallback between Polygon and yfinance, and as the source for the nightly
``options_chain_daily`` snapshot table.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from typing import Any

import requests

log = logging.getLogger("signal.options_cboe")

_CBOE_OPTIONS_URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker}.json"


def _parse_option_symbol(symbol: str, ticker: str) -> dict[str, Any] | None:
    """Parse OCC-style option symbol into type/strike/expiry.

    CBOE returns symbols like ``AAPL260612C00110000``:
      {ticker}{YYMMDD}{C|P}{strike*1000, zero-padded to 8 digits}
    """
    try:
        if not symbol.startswith(ticker):
            return None
        suffix = symbol[len(ticker) :]
        if len(suffix) < 15:
            return None
        expiry_str = suffix[:6]
        cp = suffix[6].upper()
        strike_raw = suffix[7:15]
        if cp not in ("C", "P"):
            return None
        exp_year = 2000 + int(expiry_str[:2])
        exp_month = int(expiry_str[2:4])
        exp_day = int(expiry_str[4:6])
        return {
            "option_type": "call" if cp == "C" else "put",
            "strike": int(strike_raw) / 1000.0,
            "expiration_date": date(exp_year, exp_month, exp_day),
        }
    except Exception as exc:
        log.debug("[cboe] failed to parse option symbol %s: %s", symbol, exc)
        return None


def _days_to_expiry(exp: date) -> float:
    """Return T in years; minimum one day."""
    return max((exp - date.today()).days, 1) / 365.0


def _bs_gamma(S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    """Black-Scholes gamma. Returns 0 on error."""
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.0
        import math

        d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
        return math.exp(-(d1**2) / 2) / (math.sqrt(2 * math.pi) * S * sigma * math.sqrt(T))
    except Exception:
        return 0.0


def _fetch_cboe_options_raw(ticker: str) -> dict[str, Any] | None:
    """Fetch raw CBOE options JSON. Returns None on expected failure."""
    url = _CBOE_OPTIONS_URL.format(ticker=ticker.upper())
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            log.debug("[cboe] %s: no options data available (404)", ticker)
            return None
        if resp.status_code != 200:
            log.debug("[cboe] %s: HTTP %s", ticker, resp.status_code)
            return None
        return resp.json()
    except Exception as exc:
        log.warning("[cboe] %s: fetch failed — %s", ticker, exc)
        return None


def _normalize_contracts(ticker: str, raw_options: list[dict[str, Any]], spot: float) -> list[dict[str, Any]]:
    """Normalize CBOE option rows into a uniform contract dict."""
    contracts: list[dict[str, Any]] = []
    for opt in raw_options:
        symbol = opt.get("option", "")
        parsed = _parse_option_symbol(symbol, ticker.upper())
        if not parsed:
            continue
        iv = opt.get("iv")
        iv = float(iv) if iv is not None else None
        volume = opt.get("volume")
        volume = int(volume) if volume is not None else 0
        oi = opt.get("open_interest")
        oi = int(oi) if oi is not None else 0
        delta = opt.get("delta")
        delta = float(delta) if delta is not None else None
        gamma = opt.get("gamma")
        gamma = float(gamma) if gamma is not None else None
        theta = opt.get("theta")
        theta = float(theta) if theta is not None else None
        vega = opt.get("vega")
        vega = float(vega) if vega is not None else None
        bid = opt.get("bid")
        ask = opt.get("ask")
        mid = None
        if bid is not None and ask is not None:
            bid_f = float(bid)
            ask_f = float(ask)
            if ask_f >= bid_f:
                mid = round((bid_f + ask_f) / 2.0, 4)
        contracts.append(
            {
                "symbol": symbol,
                "option_type": parsed["option_type"],
                "strike": parsed["strike"],
                "expiration_date": parsed["expiration_date"].isoformat(),
                "days_to_expiry": round(_days_to_expiry(parsed["expiration_date"]), 4),
                "bid": float(bid) if bid is not None else None,
                "ask": float(ask) if ask is not None else None,
                "mid": mid,
                "iv": iv,
                "volume": volume,
                "open_interest": oi,
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega,
            }
        )
    return contracts


def _compute_max_pain(contracts: list[dict[str, Any]], spot: float) -> float | None:
    """Max pain = strike where total option dollar value at expiry is minimized."""
    if not contracts:
        return None
    calls = [c for c in contracts if c["option_type"] == "call"]
    puts = [c for c in contracts if c["option_type"] == "put"]
    if not calls or not puts:
        return None
    strikes = sorted({c["strike"] for c in contracts})
    if not strikes:
        return None
    min_pain = float("inf")
    max_pain_strike: float | None = None
    for strike in strikes:
        pain = 0.0
        for c in calls:
            pain += max(strike - c["strike"], 0) * c["open_interest"]
        for p in puts:
            pain += max(p["strike"] - strike, 0) * p["open_interest"]
        if pain < min_pain:
            min_pain = pain
            max_pain_strike = strike
    return max_pain_strike


def fetch_cboe_options_chain(
    ticker: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Fetch and aggregate CBOE options chain for use as a live fallback.

    Returns a dict shaped like the Polygon/yfinance paths in ``services/options.py``
    so it can be dropped into ``_fetch_options`` without downstream changes.

    ``payload`` is exposed for unit tests; when None the CBOE endpoint is hit.
    """
    if payload is None:
        payload = _fetch_cboe_options_raw(ticker)
    if not payload:
        return None

    data = payload.get("data") or {}
    raw_options = data.get("options") or []
    if not raw_options:
        return None

    spot = data.get("current_price")
    try:
        spot = float(spot) if spot is not None else None
    except Exception:
        spot = None

    contracts = _normalize_contracts(ticker, raw_options, spot or 0.0)
    if not contracts:
        return None

    calls = [c for c in contracts if c["option_type"] == "call"]
    puts = [c for c in contracts if c["option_type"] == "put"]

    call_vol = sum(c["volume"] for c in calls)
    put_vol = sum(p["volume"] for p in puts)
    total_vol = call_vol + put_vol
    if total_vol < 50:
        return None

    call_oi = sum(c["open_interest"] for c in calls)
    put_oi = sum(p["open_interest"] for p in puts)
    total_oi = call_oi + put_oi

    pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None
    unusual_vol_ratio = round(total_vol / total_oi, 2) if total_oi > 0 else None

    # IV by expiry
    by_expiry: dict[str, list[float]] = defaultdict(list)
    for c in contracts:
        if c["iv"] is not None and c["iv"] > 0:
            by_expiry[c["expiration_date"]].append(c["iv"])
    sorted_exps = sorted(by_expiry.keys())
    near_iv = float(sum(by_expiry[sorted_exps[0]]) / len(by_expiry[sorted_exps[0]])) if sorted_exps else None
    far_iv = float(sum(by_expiry[sorted_exps[1]]) / len(by_expiry[sorted_exps[1]])) if len(sorted_exps) >= 2 else None
    iv_term_spike = round(near_iv / far_iv, 2) if near_iv and far_iv and far_iv > 0 else None

    all_ivs = [c["iv"] for c in contracts if c["iv"] is not None and c["iv"] > 0]
    avg_iv = round(sum(all_ivs) / len(all_ivs), 4) if all_ivs else None

    # 25-delta skew
    skew_25d = put_iv_25d = call_iv_25d = None
    if spot and spot > 0:
        put_25_ivs = [c["iv"] for c in puts if c["iv"] and 0.20 <= abs(c["delta"] or 0) <= 0.30]
        call_25_ivs = [c["iv"] for c in calls if c["iv"] and 0.20 <= abs(c["delta"] or 0) <= 0.30]
        if put_25_ivs and call_25_ivs:
            put_iv_25d = round(sum(put_25_ivs) / len(put_25_ivs), 4)
            call_iv_25d = round(sum(call_25_ivs) / len(call_25_ivs), 4)
            skew_25d = round(put_iv_25d - call_iv_25d, 4)

    # GEX proxy
    gex_total = 0.0
    if spot and spot > 0:
        for c in contracts:
            gamma = c["gamma"] or 0.0
            oi = float(c["open_interest"])
            if gamma == 0.0 or oi == 0.0:
                continue
            sign = -1 if c["option_type"] == "call" else 1
            gex_total += sign * gamma * oi * 100 * spot
    gex_total = round(gex_total, 0)

    # Sweeps
    sweep_calls, sweep_puts = [], []
    for c in contracts:
        if c["open_interest"] > 0 and c["volume"] / c["open_interest"] > 5 and c["volume"] > 200:
            entry = {
                "strike": c["strike"],
                "vol": c["volume"],
                "oi": c["open_interest"],
                "vol_oi": round(c["volume"] / c["open_interest"], 1),
                "iv": c["iv"] or 0.0,
                "expiry": c["expiration_date"],
                "itm": False,
            }
            (sweep_calls if c["option_type"] == "call" else sweep_puts).append(entry)
    sweep_calls.sort(key=lambda x: -x["vol"])
    sweep_puts.sort(key=lambda x: -x["vol"])

    # OTM volumes
    otm_call_vol = sum(c["volume"] for c in calls if spot and c["strike"] > spot)
    otm_put_vol = sum(p["volume"] for p in puts if spot and p["strike"] < spot)

    # Net delta flow
    net_delta_flow = 0.0
    for c in contracts:
        delta = c["delta"] or 0.0
        net_delta_flow += delta * c["volume"] * 100
    net_delta_flow = round(net_delta_flow, 0)
    delta_flow_ratio = round(net_delta_flow / (total_vol * 100), 3) if total_vol > 0 else None

    # Zero-DTE put ratio
    today_str = date.today().isoformat()
    zero_dte_puts = [p for p in puts if p["expiration_date"] == today_str]
    zero_dte_calls = [c for c in calls if c["expiration_date"] == today_str]
    zero_dte_ratio = (
        round(sum(p["volume"] for p in zero_dte_puts) / sum(c["volume"] for c in zero_dte_calls), 2)
        if zero_dte_calls
        else None
    )

    max_pain = _compute_max_pain(contracts, spot or 0.0)

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
        "iv_rank": None,  # historical IV rank requires accumulated history
        "skew_25d": skew_25d,
        "put_iv_25d": put_iv_25d,
        "call_iv_25d": call_iv_25d,
        "gex": gex_total,
        "net_delta_flow": net_delta_flow,
        "delta_flow_ratio": delta_flow_ratio,
        "spot": spot,
        "zero_dte_ratio": zero_dte_ratio,
        "max_pain": max_pain,
        "source": "cboe",
        "contracts": contracts,
    }


def build_options_chain_daily_row(
    ticker: str,
    snapshot_date: date,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Build a dict suitable for upserting into ``OptionsChainDaily``.

    If ``payload`` is None, the CBOE endpoint is fetched fresh.
    """
    if payload is None:
        payload = _fetch_cboe_options_raw(ticker)
    if not payload:
        return None

    data = payload.get("data") or {}
    raw_options = data.get("options") or []
    if not raw_options:
        return None

    spot = data.get("current_price")
    try:
        spot = float(spot) if spot is not None else None
    except Exception:
        spot = None

    contracts = _normalize_contracts(ticker, raw_options, spot or 0.0)
    if not contracts:
        return None

    calls = [c for c in contracts if c["option_type"] == "call"]
    puts = [c for c in contracts if c["option_type"] == "put"]

    call_vol = sum(c["volume"] for c in calls)
    put_vol = sum(p["volume"] for p in puts)
    total_vol = call_vol + put_vol
    if total_vol < 50:
        return None

    total_oi = sum(c["open_interest"] for c in calls) + sum(p["open_interest"] for p in puts)
    pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None

    by_expiry: dict[str, list[float]] = defaultdict(list)
    for c in contracts:
        if c["iv"] is not None and c["iv"] > 0:
            by_expiry[c["expiration_date"]].append(c["iv"])
    sorted_exps = sorted(by_expiry.keys())
    near_iv = float(sum(by_expiry[sorted_exps[0]]) / len(by_expiry[sorted_exps[0]])) if sorted_exps else None
    far_iv = float(sum(by_expiry[sorted_exps[1]]) / len(by_expiry[sorted_exps[1]])) if len(sorted_exps) >= 2 else None
    iv_term_spike = round(near_iv / far_iv, 2) if near_iv and far_iv and far_iv > 0 else None
    all_ivs = [c["iv"] for c in contracts if c["iv"] is not None and c["iv"] > 0]
    avg_iv = round(sum(all_ivs) / len(all_ivs), 4) if all_ivs else None

    skew_25d = None
    if spot and spot > 0:
        put_25_ivs = [c["iv"] for c in puts if c["iv"] and 0.20 <= abs(c["delta"] or 0) <= 0.30]
        call_25_ivs = [c["iv"] for c in calls if c["iv"] and 0.20 <= abs(c["delta"] or 0) <= 0.30]
        if put_25_ivs and call_25_ivs:
            skew_25d = round(sum(put_25_ivs) / len(put_25_ivs) - sum(call_25_ivs) / len(call_25_ivs), 4)

    net_gex = 0.0
    if spot and spot > 0:
        for c in contracts:
            gamma = c["gamma"] or 0.0
            oi = float(c["open_interest"])
            if gamma and oi:
                sign = -1 if c["option_type"] == "call" else 1
                net_gex += sign * gamma * oi * 100 * spot
    net_gex = round(net_gex, 0)

    max_pain = _compute_max_pain(contracts, spot or 0.0)

    return {
        "ticker": ticker.upper(),
        "date": snapshot_date,
        "contract_count": len(contracts),
        "put_call_ratio": pc_ratio,
        "total_volume": total_vol,
        "total_open_interest": total_oi,
        "avg_iv": avg_iv,
        "near_iv": near_iv,
        "far_iv": far_iv,
        "iv_term_spike": iv_term_spike,
        "iv_rank": None,
        "skew_25d": skew_25d,
        "max_pain": max_pain,
        "net_gex": net_gex,
        "spot": spot,
        "source": "cboe",
        "contracts_snapshot": contracts[:500],  # cap row size; full chain rarely needed in DB
    }
