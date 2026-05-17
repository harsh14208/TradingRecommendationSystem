"""
Macro-market context using:
  • yfinance  — VIX (^VIX), 10-Y yield (^TNX), S&P 500 (^GSPC)  [free, no key]
  • FRED API  — Fed Funds Rate, CPI  [free key, optional]

If FRED_API_KEY is blank the FRED section is silently skipped.
"""
import asyncio
import os
import ssl
import time
from typing import Optional

import aiohttp
import certifi

from services.market_data import get_history
from services.redis_cache import cache_get, cache_set

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())

_CACHE_KEY = "macro:context"
CACHE_TTL = 3600  # 1 hour — macro data is slow-moving


async def _fred(series_id: str, api_key: str) -> Optional[float]:
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={api_key}"
        f"&limit=2&sort_order=desc&file_type=json"
    )
    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                d = await r.json(content_type=None)
                return float(d["observations"][0]["value"])
    except Exception:
        return None


def _sector_rotation_stage(vix: float | None, yc_spread: float | None,
                             hyg_1m: float | None, sp500_trend: str | None) -> dict:
    """
    Map macro signals to one of four economic cycle stages.
    Returns {"stage": str, "favoured": list[str], "avoid": list[str], "confidence": int}
    """
    stage = "mid"   # default
    confidence = 0

    checks_bull = 0
    checks_bear = 0

    if sp500_trend == "up":   checks_bull += 1
    if sp500_trend == "down": checks_bear += 1

    if yc_spread is not None:
        if yc_spread > 1.0:   checks_bull += 1
        if yc_spread < 0:     checks_bear += 2  # inversion = late / recession

    if vix is not None:
        if vix < 16:  checks_bull += 1
        if vix > 28:  checks_bear += 2

    if hyg_1m is not None:
        if hyg_1m > 1:   checks_bull += 1
        if hyg_1m < -2:  checks_bear += 1

    total = checks_bull + checks_bear
    if total == 0:
        return {"stage": "mid", "favoured": ["XLK","XLY","XLC"], "avoid": [], "confidence": 0}

    bull_ratio = checks_bull / max(total, 1)

    if bull_ratio >= 0.75:
        stage = "early"   # recovery — credit improving, vol falling, curve steepening
        favoured = ["XLY", "XLF", "XLB", "XLI"]  # cyclicals, financials, materials, industrials
        avoid    = ["XLU", "XLRE"]                 # defensives lag in early cycle
        confidence = min(90, int(bull_ratio * 100))
    elif bull_ratio >= 0.5:
        stage = "mid"     # expansion — broad participation
        favoured = ["XLK", "XLI", "XLY", "XLC"]
        avoid    = []
        confidence = min(70, int(bull_ratio * 80))
    elif bull_ratio >= 0.25:
        stage = "late"    # slowdown — defensives outperform
        favoured = ["XLV", "XLP", "XLU", "XLRE"]
        avoid    = ["XLB", "XLI"]
        confidence = min(70, int((1 - bull_ratio) * 80))
    else:
        stage = "recession"
        favoured = ["XLV", "XLP", "XLU", "GLD"]
        avoid    = ["XLY", "XLF", "XLB"]
        confidence = min(90, int((1 - bull_ratio) * 100))

    return {
        "stage":     stage,
        "favoured":  favoured,
        "avoid":     avoid,
        "confidence": confidence,
        "bull_checks": checks_bull,
        "bear_checks": checks_bear,
    }


async def get_macro_context() -> dict:
    cached = await cache_get(_CACHE_KEY)
    if cached:
        return cached

    score      = 0
    rationale  = []
    result: dict = {}

    # ── VIX — Polygon primary, yfinance fallback ─────────────────────────
    # yfinance ^VIX is frequently rate-limited and returns empty DataFrames.
    # Polygon's VIX feed (confirmed free-tier accessible) is more reliable.
    try:
        vix_df = None
        _poly_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
        if _poly_key:
            try:
                from services.polygon_client import get_polygon_history
                vix_df = await get_polygon_history("I:VXN", period="5d", interval="1d")
                if vix_df is None or vix_df.empty:
                    vix_df = await get_polygon_history("^VIX", period="5d", interval="1d")
            except Exception:
                vix_df = None
        if vix_df is None or vix_df.empty:
            vix_df = await get_history("^VIX", period="5d", interval="1d")
        if vix_df is not None and not vix_df.empty:
            vix = round(float(vix_df["Close"].iloc[-1]), 2)
            result["vix"] = vix
            if vix > 30:
                score -= 12
                rationale.append({
                    "src": "Macro", "head": f"VIX Spiked to {vix:.1f} — High Fear",
                    "body": "Elevated VIX signals market panic. Reduce position size; favour tight stops.",
                    "sentiment": "neg", "meta": f"VIX = {vix:.1f}  (>30 = danger zone)",
                })
            elif vix > 20:
                score -= 5
                rationale.append({
                    "src": "Macro", "head": f"VIX Elevated ({vix:.1f})",
                    "body": "Above-average volatility — markets cautious.",
                    "sentiment": "neg", "meta": f"VIX = {vix:.1f}",
                })
            elif vix < 14:
                score += 6
                rationale.append({
                    "src": "Macro", "head": f"VIX Low at {vix:.1f} — Calm Markets",
                    "body": "Low volatility favours trend-following and momentum strategies.",
                    "sentiment": "pos", "meta": f"VIX = {vix:.1f}  (<14 = low fear)",
                })
    except Exception as e:
        print(f"[macro] VIX: {e}")

    # ── 10-Year Treasury yield ────────────────────────────────────────────
    try:
        t10_df = await get_history("^TNX", period="5d", interval="1d")
        if t10_df is not None and not t10_df.empty:
            t10y = round(float(t10_df["Close"].iloc[-1]), 3)
            result["t10y"] = t10y
            if t10y > 4.8:
                score -= 8
                rationale.append({
                    "src": "Macro", "head": f"10-Y Yield High at {t10y:.2f}%",
                    "body": "High long-term rates compress equity valuations and increase borrowing costs.",
                    "sentiment": "neg", "meta": f"^TNX = {t10y:.2f}%",
                })
            elif t10y < 3.5:
                score += 5
                rationale.append({
                    "src": "Macro", "head": f"10-Y Yield Low at {t10y:.2f}%",
                    "body": "Low rates reduce the discount rate on future earnings, boosting equity valuations.",
                    "sentiment": "pos", "meta": f"^TNX = {t10y:.2f}%",
                })
    except Exception as e:
        print(f"[macro] TNX: {e}")

    # ── S&P 500 regime + SPY 1-month return ──────────────────────────────
    try:
        sp_df = await get_history("^GSPC", period="3mo", interval="1d")
        if sp_df is not None and len(sp_df) >= 50:
            sma50 = float(sp_df["Close"].rolling(50).mean().iloc[-1])
            price = float(sp_df["Close"].iloc[-1])
            trend = "up" if price > sma50 else "down"
            result["sp500_trend"] = trend
            result["sp500"]       = round(price, 2)
            if trend == "up":
                score += 6
            else:
                score -= 6
                rationale.append({
                    "src": "Macro", "head": "S&P 500 Below 50-DMA",
                    "body": "Broad market in short-term downtrend. Higher risk for long positions.",
                    "sentiment": "neg", "meta": f"S&P {price:.0f} < 50-DMA {sma50:.0f}",
                })
            # Store 1-month SPY return so signal engine can compute relative strength
            if len(sp_df) >= 21:
                spy_1m = (sp_df["Close"].iloc[-1] / sp_df["Close"].iloc[-21] - 1) * 100
                result["spy_1m_ret"] = round(float(spy_1m), 2)
    except Exception as e:
        print(f"[macro] SP500: {e}")

    # ── FRED (optional) ───────────────────────────────────────────────────
    try:
        from config import get_settings
        key = get_settings().fred_api_key
        if key:
            fed_rate, cpi = await asyncio.gather(
                _fred("FEDFUNDS", key),
                _fred("CPIAUCSL", key),
            )
            if fed_rate is not None:
                result["fed_funds"] = fed_rate
                if fed_rate > 5.0:
                    score -= 7
                    rationale.append({
                        "src": "FRED", "head": f"Fed Funds Rate at {fed_rate:.2f}%",
                        "body": "Restrictive monetary policy. Higher rates slow growth and hurt risk assets.",
                        "sentiment": "neg", "meta": f"FEDFUNDS = {fed_rate:.2f}%",
                    })
                elif fed_rate < 2.0:
                    score += 5
            if cpi is not None:
                result["cpi"] = cpi
    except Exception as e:
        print(f"[macro] FRED: {e}")

    # ── HYG — High-Yield Credit Stress (free via yfinance) ──────────────
    try:
        hyg_df = await get_history("HYG", period="3mo", interval="1d")
        if hyg_df is not None and len(hyg_df) >= 21:
            hyg_1m = (float(hyg_df["Close"].iloc[-1]) / float(hyg_df["Close"].iloc[-21]) - 1) * 100
            result["hyg_1m_ret"] = round(hyg_1m, 2)
    except Exception as e:
        print(f"[macro] HYG: {e}")

    # ── VIX term structure (VIX vs VIX3M) ────────────────────────────────
    try:
        vix3m_df = await get_history("^VIX3M", period="5d", interval="1d")
        vix_now  = result.get("vix")
        if vix3m_df is not None and not vix3m_df.empty and vix_now:
            vix3m = round(float(vix3m_df["Close"].iloc[-1]), 2)
            result["vix3m"] = vix3m
            ratio = round(vix_now / vix3m, 3) if vix3m > 0 else None
            result["vix_term_ratio"] = ratio
            if ratio is not None:
                if ratio > 1.10:   # backwardation — panic
                    score += 7
                    rationale.append({
                        "src": "Macro", "head": f"VIX Backwardation ({ratio:.2f}×) — Market Panic",
                        "body": f"VIX ({vix_now:.1f}) exceeds 3-month VIX ({vix3m:.1f}). Near-term fear outpaces long-term — historically a contrarian buying opportunity as panic peaks.",
                        "sentiment": "pos", "meta": f"VIX/VIX3M = {ratio:.2f}×",
                    })
                elif ratio < 0.85:  # steep contango — complacency
                    score -= 4
                    rationale.append({
                        "src": "Macro", "head": f"VIX Steep Contango — Complacency",
                        "body": f"3-month VIX ({vix3m:.1f}) well above spot VIX ({vix_now:.1f}). Market is unusually calm near-term — complacency often precedes corrections.",
                        "sentiment": "neg", "meta": f"VIX/VIX3M = {ratio:.2f}×",
                    })
    except Exception as e:
        print(f"[macro] VIX3M: {e}")

    # ── Yield curve (2Y-10Y spread) ───────────────────────────────────────
    try:
        t2y_df = await get_history("^IRX", period="5d", interval="1d")
        t10y   = result.get("t10y")
        if t2y_df is not None and not t2y_df.empty and t10y:
            t2y    = round(float(t2y_df["Close"].iloc[-1]) / 10, 3)  # ^IRX is in basis pts / 10
            spread = round(t10y - t2y, 3)
            result["t2y"]    = t2y
            result["yc_spread"] = spread
            if spread < 0:
                score -= 8
                rationale.append({
                    "src": "Macro", "head": f"Yield Curve Inverted ({spread:+.2f}%)",
                    "body": f"2Y yield ({t2y:.2f}%) exceeds 10Y yield ({t10y:.2f}%). An inverted curve has preceded every US recession since 1955. Elevated risk for equities.",
                    "sentiment": "neg", "meta": f"2Y-10Y = {spread:+.2f}%",
                })
            elif spread > 1.0:
                score += 5
                rationale.append({
                    "src": "Macro", "head": f"Healthy Yield Curve (+{spread:.2f}%)",
                    "body": f"10Y yield ({t10y:.2f}%) comfortably above 2Y ({t2y:.2f}%). Normal upward-sloping curve signals healthy growth expectations.",
                    "sentiment": "pos", "meta": f"2Y-10Y = +{spread:.2f}%",
                })
    except Exception as e:
        print(f"[macro] IRX: {e}")

    # ── DXY — US Dollar Index ─────────────────────────────────────────────
    try:
        dxy_df = await get_history("DX-Y.NYB", period="3mo", interval="1d")
        if dxy_df is not None and len(dxy_df) >= 21:
            dxy_now  = round(float(dxy_df["Close"].iloc[-1]), 2)
            dxy_1m   = round((dxy_now / float(dxy_df["Close"].iloc[-21]) - 1) * 100, 2)
            result["dxy"]      = dxy_now
            result["dxy_1m"]   = dxy_1m
    except Exception as e:
        print(f"[macro] DXY: {e}")

    # ── Copper/Gold ratio (growth vs safety demand) ───────────────────────
    try:
        cu_df, au_df = await asyncio.gather(
            get_history("HG=F", period="3mo", interval="1d"),
            get_history("GC=F", period="3mo", interval="1d"),
        )
        if (cu_df is not None and len(cu_df) >= 21 and
                au_df is not None and len(au_df) >= 21):
            cg_now  = float(cu_df["Close"].iloc[-1]) / float(au_df["Close"].iloc[-1])
            cg_1m   = float(cu_df["Close"].iloc[-21]) / float(au_df["Close"].iloc[-21])
            cg_chg  = round((cg_now / cg_1m - 1) * 100, 2)
            result["cu_gold_ratio"] = round(cg_now, 6)
            result["cu_gold_1m"]    = cg_chg
            if cg_chg > 4:
                score += 6
                rationale.append({
                    "src": "Macro", "head": f"Copper/Gold Ratio Rising (+{cg_chg:.1f}% 1M)",
                    "body": "Rising copper relative to gold signals expanding industrial demand and risk-on appetite. Historically leads equity gains by 2–4 weeks.",
                    "sentiment": "pos", "meta": f"Cu/Au 1M: +{cg_chg:.1f}%",
                })
            elif cg_chg < -4:
                score -= 5
                rationale.append({
                    "src": "Macro", "head": f"Copper/Gold Ratio Falling ({cg_chg:.1f}% 1M)",
                    "body": "Copper underperforming gold signals deteriorating growth expectations and risk-off rotation into safety assets.",
                    "sentiment": "neg", "meta": f"Cu/Au 1M: {cg_chg:.1f}%",
                })
    except Exception as e:
        print(f"[macro] Cu/Au: {e}")

    # ── Macro News Sentiment via SPY/QQQ Polygon news ───────────────────
    # SPY/QQQ ETF-level news acts as a market-wide fear/greed proxy.
    # When avg sentiment < -0.3 AND VIX > 20 → additional -8pp BUY cap applied
    # downstream by signal_engine. We compute the sentiment here and store it.
    try:
        _poly_key2 = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
        if _poly_key2:
            _ssl2 = ssl.create_default_context(cafile=certifi.where())
            _news_scores: list[float] = []
            _keywords_pos = {"rally", "surge", "gain", "rise", "bull", "record", "high",
                             "strong", "beat", "up", "positive", "growth"}
            _keywords_neg = {"fall", "drop", "crash", "recession", "bear", "low", "weak",
                             "miss", "down", "negative", "decline", "sell", "fear", "risk"}
            async with aiohttp.ClientSession() as _ns:
                for _etf in ("SPY", "QQQ"):
                    async with _ns.get(
                        "https://api.polygon.io/v2/reference/news",
                        params={"ticker": _etf, "limit": 5, "order": "desc",
                                "sort": "published_utc", "apiKey": _poly_key2},
                        ssl=_ssl2, timeout=aiohttp.ClientTimeout(total=6)
                    ) as _nr:
                        if _nr.status == 200:
                            _nd = await _nr.json()
                            for _art in (_nd.get("results") or []):
                                _title = (_art.get("title") or "").lower()
                                _words = set(_title.split())
                                _pos = len(_words & _keywords_pos)
                                _neg = len(_words & _keywords_neg)
                                if _pos + _neg > 0:
                                    _news_scores.append((_pos - _neg) / (_pos + _neg))
            if _news_scores:
                _avg_sentiment = sum(_news_scores) / len(_news_scores)
                result["macro_news_sentiment"] = round(_avg_sentiment, 3)
                result["macro_news_count"]     = len(_news_scores)
    except Exception:
        pass

    # ── Sector rotation stage ─────────────────────────────────────────────
    result["sector_rotation"] = _sector_rotation_stage(
        vix=result.get("vix"),
        yc_spread=result.get("yc_spread"),
        hyg_1m=result.get("hyg_1m_ret"),
        sp500_trend=result.get("sp500_trend"),
    )

    result["macro_score"] = score
    result["rationale"]   = rationale

    # ── Market status from Polygon.io ─────────────────────────────────────
    # Replaces the time-heuristic check with authoritative NYSE open/close state.
    try:
        import os, ssl, certifi, aiohttp
        _poly_key = os.getenv("POLYGON_API_KEY") or os.getenv("MASSIVE_API_KEY") or ""
        if _poly_key:
            _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
            async with aiohttp.ClientSession() as _sess:
                async with _sess.get(
                    "https://api.polygon.io/v1/marketstatus/now",
                    params={"apiKey": _poly_key}, ssl=_ssl_ctx,
                    timeout=aiohttp.ClientTimeout(total=4)
                ) as _r:
                    if _r.status == 200:
                        _ms = await _r.json()
                        _nyse = (_ms.get("exchanges") or {}).get("nyse", "")
                        result["market_open"]  = _nyse == "open"
                        result["after_hours"]  = bool(_ms.get("afterHours", False))
                        result["early_hours"]  = bool(_ms.get("earlyHours", False))
    except Exception:
        # Fall back to time-based detection if Polygon is unavailable
        import pytz
        from datetime import datetime as _dt, time as _dtime
        _et  = pytz.timezone("America/New_York")
        _now = _dt.now(_et).time()
        result.setdefault("market_open", _dtime(9, 30) <= _now <= _dtime(16, 0))

    await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
    return result
