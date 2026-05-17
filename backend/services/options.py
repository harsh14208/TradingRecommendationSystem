"""
Options flow signals via yfinance (free, no API key).

Enhanced detection across multiple expiries:
  - Cross-expiry put/call ratio
  - Sweep detection: single-strike vol >> OI (new conviction money)
  - OTM call/put spike: large directional bets on short-dated options
  - IV term structure: near-term IV spike vs back-month (event proximity)
  - Dark pool proxy: large block trades on single strike
"""
import asyncio
import math
import time as _time
from concurrent.futures import ThreadPoolExecutor

import yfinance as yf

from services.market_data import _session, _retry


def _bs_gamma(S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    """Black-Scholes gamma. Returns 0 on error."""
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.0
        d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
        return math.exp(-d1 ** 2 / 2) / (math.sqrt(2 * math.pi) * S * sigma * math.sqrt(T))
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
        d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        phi_d1 = math.exp(-d1 ** 2 / 2) / math.sqrt(2 * math.pi)
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
        d1   = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
        d2   = d1 - sigma * math.sqrt(T)
        phi  = math.exp(-d1 ** 2 / 2) / math.sqrt(2 * math.pi)
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
        K   = opt.get("strike", 0)
        T   = max(opt.get("expiry_days", 0), 0.1) / 365.0
        sig = opt.get("iv", 0)
        oi  = opt.get("oi", 0)
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
    charm_sig = "bullish" if net_charm > 0  else "bearish" if net_charm < 0  else "neutral"

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
        "net_vanna":    round(net_vanna, 4),
        "net_charm":    round(net_charm, 6),
        "vanna_signal": vanna_sig,
        "charm_signal": charm_sig,
        "interpretation": " ".join(interp_parts) or "Neutral dealer positioning.",
    }

_executor   = ThreadPoolExecutor(max_workers=3)
_opt_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL   = 2400  # 40 min — more frequent refresh for intraday sweeps

# Per-ticker rolling IV history for IV Rank computation (populated over time)
_iv_history: dict[str, list[float]] = {}
_IV_HISTORY_MAX = 252


def _fetch_options(ticker: str) -> dict:
    cached = _opt_cache.get(ticker)
    if cached and _time.time() - cached[1] < CACHE_TTL:
        return cached[0]

    try:
        t           = yf.Ticker(ticker, session=_session)
        expirations = _retry(lambda: t.options)
        if not expirations:
            return {}

        # Analyse first 3 expiries (catches short-dated sweep activity)
        expiries_to_check = expirations[:3]
        all_calls = []
        all_puts  = []
        chains    = []

        for exp in expiries_to_check:
            try:
                chain = _retry(lambda e=exp: t.option_chain(e))
                if chain and not chain.calls.empty:
                    calls_df = chain.calls.copy()
                    puts_df  = chain.puts.copy()
                    calls_df["expiry"] = exp
                    puts_df["expiry"]  = exp
                    all_calls.append(calls_df)
                    all_puts.append(puts_df)
                    chains.append((exp, chain.calls, chain.puts))
            except Exception:
                continue

        if not all_calls:
            return {}

        import pandas as pd
        calls = pd.concat(all_calls, ignore_index=True)
        puts  = pd.concat(all_puts,  ignore_index=True)

        call_vol  = int(calls["volume"].fillna(0).sum())
        put_vol   = int(puts["volume"].fillna(0).sum())
        call_oi   = int(calls["openInterest"].fillna(0).sum())
        put_oi    = int(puts["openInterest"].fillna(0).sum())
        total_vol = call_vol + put_vol

        if total_vol < 50:
            return {}

        pc_ratio = round(put_vol / call_vol, 3) if call_vol > 0 else None

        # ── Sweep detection: find individual strikes with vol >> OI ─────────
        sweep_calls = []
        sweep_puts  = []
        for df, side in [(calls, "call"), (puts, "put")]:
            df = df[df["openInterest"].fillna(0) > 0].copy()
            df["vol_oi"] = df["volume"].fillna(0) / df["openInterest"]
            big = df[(df["vol_oi"] > 5) & (df["volume"].fillna(0) > 200)]
            for _, row in big.iterrows():
                entry = {
                    "strike":    float(row.get("strike", 0)),
                    "vol":       int(row.get("volume", 0)),
                    "oi":        int(row.get("openInterest", 0)),
                    "vol_oi":    round(float(row["vol_oi"]), 1),
                    "iv":        float(row.get("impliedVolatility", 0)),
                    "expiry":    row.get("expiry", ""),
                    "itm":       bool(row.get("inTheMoney", False)),
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
        otm_puts  = puts[ (puts["inTheMoney"].fillna(True)  == False)]
        otm_call_vol = int(otm_calls["volume"].fillna(0).sum())
        otm_put_vol  = int(otm_puts["volume"].fillna(0).sum())

        # ── IV calculations ───────────────────────────────────────────────────
        near_iv = None
        far_iv  = None
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
                from datetime import datetime
                exp_dt = datetime.strptime(exp_str, "%Y-%m-%d")
                T = max((exp_dt - datetime.utcnow()).days / 365.0, 1 / 365)
                spot = None
                # Fallback: use median strike as spot proxy
                if spot is None:
                    spot = float(c_df["strike"].median()) if not c_df.empty else 0
                if spot > 0:
                    for df_side, sign in [(c_df, -1), (p_df, 1)]:
                        for _, row in df_side.iterrows():
                            K   = float(row.get("strike", 0))
                            oi  = float(row.get("openInterest", 0) or 0)
                            iv  = float(row.get("impliedVolatility", 0) or 0)
                            if K > 0 and oi > 0 and iv > 0:
                                g = _bs_gamma(spot, K, T, iv)
                                gex_total += sign * g * oi * 100 * spot
        except Exception:
            pass
        gex_total = round(gex_total, 0)

        total_oi = call_oi + put_oi
        unusual_vol_ratio = round(total_vol / total_oi, 2) if total_oi > 0 else None

        # ── Avg IV across all near-term ATM options ───────────────────────────
        try:
            atm_iv_vals = pd.concat([
                calls["impliedVolatility"].dropna().head(5),
                puts["impliedVolatility"].dropna().head(5),
            ])
            avg_iv = round(float(atm_iv_vals.mean()), 4) if len(atm_iv_vals) > 0 else None
        except Exception:
            avg_iv = None

        # ── Track IV history for IV Rank ─────────────────────────────────
        if avg_iv and avg_iv > 0:
            hist = _iv_history.setdefault(ticker, [])
            hist.append(avg_iv)
            if len(hist) > _IV_HISTORY_MAX:
                _iv_history[ticker] = hist[-_IV_HISTORY_MAX:]

        # ── 25-delta approximation skew ───────────────────────────────────
        skew_25d   = None
        put_iv_25d = None
        call_iv_25d = None
        try:
            spot = None
            # Approximate spot from ATM strike (nearest OI weighted)
            if not calls.empty and "strike" in calls.columns:
                atm_idx = (calls["strike"] - calls["strike"].median()).abs().idxmin()
                spot = float(calls.loc[atm_idx, "strike"])
            if spot and spot > 0:
                call_25 = calls[
                    (calls["strike"] >= spot * 1.03) & (calls["strike"] <= spot * 1.10)
                ]
                put_25 = puts[
                    (puts["strike"] >= spot * 0.90) & (puts["strike"] <= spot * 0.97)
                ]
                c25_iv = float(call_25["impliedVolatility"].dropna().mean()) if not call_25.empty else None
                p25_iv = float(put_25["impliedVolatility"].dropna().mean()) if not put_25.empty else None
                if c25_iv and p25_iv and c25_iv > 0:
                    skew_25d   = round(p25_iv - c25_iv, 4)
                    put_iv_25d  = round(p25_iv, 4)
                    call_iv_25d = round(c25_iv, 4)
        except Exception:
            pass

        # ── IV Rank ───────────────────────────────────────────────────────
        iv_rank = None
        if avg_iv:
            iv_hist = _iv_history.get(ticker, [])
            if len(iv_hist) >= 10:
                iv_low  = min(iv_hist)
                iv_high = max(iv_hist)
                iv_rank = round((avg_iv - iv_low) / (iv_high - iv_low) * 100, 1) if iv_high > iv_low else 50.0

        result = {
            "call_vol":          call_vol,
            "put_vol":           put_vol,
            "pc_ratio":          pc_ratio,
            "total_vol":         total_vol,
            "unusual_vol_ratio": unusual_vol_ratio,
            "avg_iv":            avg_iv,
            "near_iv":           near_iv,
            "far_iv":            far_iv,
            "iv_term_spike":     iv_term_spike,
            "otm_call_vol":      otm_call_vol,
            "otm_put_vol":       otm_put_vol,
            "sweep_calls":       sweep_calls[:3],
            "sweep_puts":        sweep_puts[:3],
            "expiry":            expirations[0],
            "expiries_checked":  len(chains),
            "iv_rank":           iv_rank,
            "skew_25d":          skew_25d,
            "put_iv_25d":        put_iv_25d,
            "call_iv_25d":       call_iv_25d,
            "gex":               gex_total,
        }
        _opt_cache[ticker] = (result, _time.time())
        return result

    except Exception as e:
        print(f"[options] {ticker}: {e}")
        return {}


async def get_options_flow(ticker: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(_executor, _fetch_options, ticker)


def score_options(opt: dict) -> tuple[float, list[dict]]:
    """Return (score_delta, rationale_items) from enhanced options data."""
    if not opt:
        return 0.0, []

    score     = 0.0
    rationale = []
    pc        = opt.get("pc_ratio")
    uv        = opt.get("unusual_vol_ratio")
    iv        = opt.get("avg_iv")
    call_vol  = opt.get("call_vol", 0)
    put_vol   = opt.get("put_vol", 0)
    sweep_calls = opt.get("sweep_calls", [])
    sweep_puts  = opt.get("sweep_puts", [])
    otm_cv    = opt.get("otm_call_vol", 0)
    otm_pv    = opt.get("otm_put_vol", 0)
    iv_spike  = opt.get("iv_term_spike")

    # ── Put/Call ratio ────────────────────────────────────────────────────────
    if pc is not None:
        if pc > 2.0:
            score += 10
            rationale.append({
                "src": "Options", "head": f"Extreme Put/Call {pc:.2f} — Contrarian Bullish",
                "body": f"Extreme put buying (P/C = {pc:.2f}) across {opt.get('expiries_checked',1)} expiries. "
                        f"This level of fear is historically a contrarian buy signal.",
                "sentiment": "pos", "meta": f"P/C = {pc:.2f}"
            })
        elif pc > 1.4:
            score += 5
        elif pc < 0.45:
            score -= 12
            rationale.append({
                "src": "Options", "head": f"Extreme Call/Put {pc:.2f} — Contrarian Bearish",
                "body": f"Call-side mania (P/C = {pc:.2f}) across {opt.get('expiries_checked',1)} expiries. "
                        f"Excessive call buying often precedes reversals.",
                "sentiment": "neg", "meta": f"P/C = {pc:.2f}"
            })
        elif pc < 0.65:
            score -= 6

    # ── Large call sweeps (institutional directional bet) ─────────────────────
    if sweep_calls:
        top = sweep_calls[0]
        score += min(12, top["vol_oi"] * 1.5)
        itm_label = "ITM" if top["itm"] else "OTM"
        rationale.append({
            "src": "Options", "head": f"Large Call Sweep — ${top['strike']:.0f} {itm_label}",
            "body": f"Single-strike call sweep: {top['vol']:,} contracts traded vs {top['oi']:,} OI "
                    f"({top['vol_oi']:.1f}× OI) — expiry {top['expiry']}. "
                    f"IV on this strike: {top['iv']*100:.0f}%. "
                    "Large single-strike sweeps often indicate institutional directional conviction.",
            "sentiment": "pos", "meta": f"Vol/OI = {top['vol_oi']:.1f}× | {top['vol']:,} contracts"
        })

    # ── Large put sweeps ──────────────────────────────────────────────────────
    if sweep_puts:
        top = sweep_puts[0]
        score -= min(12, top["vol_oi"] * 1.5)
        itm_label = "ITM" if top["itm"] else "OTM"
        rationale.append({
            "src": "Options", "head": f"Large Put Sweep — ${top['strike']:.0f} {itm_label}",
            "body": f"Single-strike put sweep: {top['vol']:,} contracts vs {top['oi']:,} OI "
                    f"({top['vol_oi']:.1f}× OI) — expiry {top['expiry']}. "
                    "Large put sweeps suggest protection buying or directional short bets by institutions.",
            "sentiment": "neg", "meta": f"Vol/OI = {top['vol_oi']:.1f}× | {top['vol']:,} contracts"
        })

    # ── OTM call volume spike (speculative call buying) ───────────────────────
    if otm_cv > 0 and call_vol > 0:
        otm_call_ratio = otm_cv / call_vol
        if otm_call_ratio > 0.65 and otm_cv > 500:
            score += 6
            rationale.append({
                "src": "Options", "head": f"OTM Call Buying Surge — {otm_cv:,} contracts",
                "body": f"{otm_call_ratio*100:.0f}% of call volume is OTM ({otm_cv:,} contracts). "
                        "Elevated OTM call activity often precedes bullish moves as traders position for upside.",
                "sentiment": "pos", "meta": f"OTM calls: {otm_cv:,} / total calls: {call_vol:,}"
            })

    # ── OTM put spike (hedging activity) ─────────────────────────────────────
    if otm_pv > 0 and put_vol > 0:
        otm_put_ratio = otm_pv / put_vol
        if otm_put_ratio > 0.70 and otm_pv > 500:
            score -= 5
            rationale.append({
                "src": "Options", "head": f"OTM Put Hedging Spike — {otm_pv:,} contracts",
                "body": f"{otm_put_ratio*100:.0f}% of put volume is OTM ({otm_pv:,} contracts). "
                        "Elevated OTM put activity suggests institutional hedging ahead of expected downside.",
                "sentiment": "neg", "meta": f"OTM puts: {otm_pv:,} / total puts: {put_vol:,}"
            })

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
        rationale.append({
            "src": "Options", "head": f"Unusual Options Activity — {opt.get('total_vol',0):,} contracts",
            "body": f"Options volume is {uv:.1f}× total open interest — fresh {direction} positioning across "
                    f"{opt.get('expiries_checked',1)} expiries. Institutional money entering new positions.",
            "sentiment": "pos" if bias > 0 else "neg",
            "meta": f"Vol/OI = {uv:.1f}× | {opt.get('total_vol',0):,} total contracts"
        })

    # ── Near-term IV term structure spike (event risk) ────────────────────────
    if iv_spike is not None and iv_spike > 1.5:
        rationale.append({
            "src": "Options", "head": f"Near-term IV Spike ({iv_spike:.1f}× back-month)",
            "body": f"Short-dated IV is {iv_spike:.1f}× the next expiry's IV. "
                    "The market is pricing a large near-term move. "
                    "Check for upcoming earnings, FDA announcements, or macro events.",
            "sentiment": "neg", "meta": f"Near IV / Far IV = {iv_spike:.1f}×"
        })

    # ── Flat IV (low IV = opportunity) ────────────────────────────────────────
    if iv is not None and iv < 0.20 and uv is not None and uv > 2:
        score += 3
        rationale.append({
            "src": "Options", "head": f"Low IV ({iv*100:.0f}%) with Active Volume",
            "body": f"Implied volatility is only {iv*100:.0f}% while volume is elevated. "
                    "Low IV with high activity suggests informed buying without panic premium.",
            "sentiment": "pos", "meta": f"IV = {iv*100:.0f}%"
        })

    elif iv is not None and iv > 0.70:
        rationale.append({
            "src": "Options", "head": f"Very High Implied Volatility ({iv*100:.0f}%)",
            "body": f"Options are pricing {iv*100:.0f}% annualised vol — significantly elevated. "
                    "Reduce position size; the market is pricing a large move. Premium is expensive.",
            "sentiment": "neg", "meta": f"Avg IV = {iv*100:.0f}%"
        })

    # ── IV Rank (expensive or cheap volatility) ───────────────────────────
    iv_rank   = opt.get("iv_rank")
    skew_25d  = opt.get("skew_25d")
    if iv_rank is not None:
        if iv_rank >= 80:
            rationale.append({
                "src": "Options", "head": f"IV Rank {iv_rank:.0f}% — Expensive Volatility",
                "body": f"Options are priced at the {iv_rank:.0f}th percentile of their 52-week range. "
                        "Directional plays are expensive; premium sellers have edge. Adjust position sizing down.",
                "sentiment": "neg", "meta": f"IVR = {iv_rank:.0f}%",
            })
        elif iv_rank <= 20:
            score += 4
            rationale.append({
                "src": "Options", "head": f"IV Rank {iv_rank:.0f}% — Cheap Volatility",
                "body": f"Options are at the {iv_rank:.0f}th percentile of their 52-week range — historically cheap. "
                        "Long options strategies have favourable risk/reward. Good time for defined-risk trades.",
                "sentiment": "pos", "meta": f"IVR = {iv_rank:.0f}%",
            })

    # ── 25-delta put/call skew ─────────────────────────────────────────────
    if skew_25d is not None:
        if skew_25d > 0.10:   # puts much more expensive than calls
            score -= 4
            rationale.append({
                "src": "Options", "head": f"High Put Skew ({skew_25d*100:.0f}pp) — Hedging Demand",
                "body": f"25-delta puts carry {skew_25d*100:.0f} percentage points more IV than equivalent calls. "
                        "Elevated put skew indicates institutional hedging — smart money protecting longs.",
                "sentiment": "neg", "meta": f"25d skew: +{skew_25d*100:.0f}pp",
            })
        elif skew_25d < -0.05:  # calls more expensive than puts — unusual
            score += 5
            rationale.append({
                "src": "Options", "head": f"Inverted Skew — Call Demand Unusual",
                "body": f"25-delta calls carry more IV than equivalent puts ({abs(skew_25d)*100:.0f}pp premium). "
                        "Inverted skew is rare and signals aggressive upside positioning.",
                "sentiment": "pos", "meta": f"25d skew: {skew_25d*100:.0f}pp",
            })

    # ── Gamma Exposure (GEX) ─────────────────────────────────────────────────
    gex = opt.get("gex", 0)
    if gex != 0:
        gex_b = gex / 1e9  # normalise to billions
        if gex_b > 0.5:
            rationale.append({
                "src":  "Options",
                "head": f"Positive GEX +${gex_b:.1f}B — Price Gravity",
                "body": ("Dealers are net long gamma. As price rises they sell, as it falls they buy — "
                         "this creates gravitational pull toward high-OI strikes. Expect mean-reversion, "
                         "lower realised vol, and range-bound price action."),
                "sentiment": "neu",
                "meta": f"GEX = +${gex_b:.1f}B",
            })
        elif gex_b < -0.5:
            score -= 3
            rationale.append({
                "src":  "Options",
                "head": f"Negative GEX −${abs(gex_b):.1f}B — Trend Amplification",
                "body": ("Dealers are net short gamma. As price moves in any direction they must follow "
                         "— amplifying the move. Negative GEX environments see higher realised vol and "
                         "sharp directional moves. Favour momentum entries, widen stops."),
                "sentiment": "neg",
                "meta": f"GEX = −${abs(gex_b):.1f}B",
            })

    # ── Vanna & Charm Dealer Positioning ─────────────────────────────────────
    # Build a simplified chain from the expiry data in opt dict for V/C computation.
    spot = opt.get("spot") or opt.get("price") or 0
    chains_raw = opt.get("chains_data") or []
    if spot > 0 and chains_raw:
        simple_chain = []
        for exp_data in chains_raw[:2]:  # use nearest 2 expiries for relevance
            dte   = exp_data.get("dte", 30)
            calls = exp_data.get("calls") or []
            puts  = exp_data.get("puts")  or []
            for c in calls[:5]:  # top 5 OI strikes per expiry
                iv_ = c.get("impliedVolatility", 0) or 0
                if iv_ > 0:
                    simple_chain.append({
                        "strike": c.get("strike", spot), "expiry_days": dte,
                        "iv": iv_, "oi": c.get("openInterest", 0) or 0,
                        "option_type": "call",
                    })
            for p in puts[:5]:
                iv_ = p.get("impliedVolatility", 0) or 0
                if iv_ > 0:
                    simple_chain.append({
                        "strike": p.get("strike", spot), "expiry_days": dte,
                        "iv": iv_, "oi": p.get("openInterest", 0) or 0,
                        "option_type": "put",
                    })
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
                        rationale.append({
                            "src": "Options",
                            "head": f"Vanna Exposure {dp['vanna_signal'].capitalize()} ({net_v:+.2f})",
                            "body": dp["interpretation"],
                            "sentiment": "pos" if net_v > 0 else "neg",
                            "meta": f"net_vanna={net_v:+.2f} net_charm={net_c:+.4f}/day",
                        })
                # Charm: additional ±2 pts
                if abs(net_c) > 0.0001:
                    c_score = max(-2, min(2, -net_c * 5000))  # normalise to ±2 pts
                    score += c_score
                    if abs(c_score) >= 0.5:
                        rationale.append({
                            "src": "Options",
                            "head": f"Charm Flow {dp['charm_signal'].capitalize()} ({net_c:+.5f}/day)",
                            "body": (f"Time decay {'adds' if c_score > 0 else 'removes'} dealer delta "
                                     f"daily — creating structural {'buy' if c_score > 0 else 'sell'} pressure."),
                            "sentiment": "pos" if c_score > 0 else "neg",
                            "meta": f"net_charm={net_c:+.5f}/day",
                        })
            except Exception:
                pass

    return round(score, 1), rationale
