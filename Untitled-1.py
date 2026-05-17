"""
Signal generation engine.

Per-scan market-wide context (Fear & Greed, Macro) is fetched ONCE by the
scanner and passed in via `market_ctx`.  Per-ticker data (technicals, news,
EDGAR insider activity) is fetched concurrently for each ticker.
"""
import asyncio
from datetime import datetime, time as dtime
from typing import Optional
import pytz

from services.google_trends import get_google_trends
from services.quiverquant import get_congress_signal

_ET = pytz.timezone("America/New_York")

# Per-ticker analyst target cache with TTL: {ticker: {"mean": float, "count": int, "ts": float}}
_analyst_cache: dict[str, dict] = {}
_ANALYST_CACHE_TTL = 3600  # 1 hour — invalidate stale entries

def _current_session() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):  return "pre"
    if dtime(9, 30) <= t < dtime(16, 0): return "regular"
    if dtime(16, 0) <= t < dtime(20, 0): return "after"
    return "closed"

import pandas as pd

from services.earnings import get_earnings_calendar, get_earnings_surprise
from services.edgar import get_insider_activity
from services.fundamentals import get_fundamentals
from services.market_data import get_history, get_info
from services.news import get_analyst_recs, get_company_news
from services.news_scraper import get_scraped_news
from services.options import get_options_flow, score_options
from services.sector import get_sector_relative_strength
from services.social import get_social_sentiment
from services.technicals import calculate_indicators


def _score_to_action(score: float, agreement: int = 0) -> tuple[str, float]:
    import math
    abs_s = abs(score)
    # Sigmoid approaching ~95% asymptote. No hard ceiling — very strong multi-source
    # signals can reach the high 80s / low 90s naturally.
    # score=25→~57%, score=40→~66%, score=60→~74%, score=90→~83%, score=150→~91%
    agreement_bonus = min(5.0, agreement * 0.4)
    raw = 40.0 + 52.0 * (1.0 - math.exp(-abs_s / 65.0)) + agreement_bonus
    confidence = round(min(97.0, raw), 1)   # absolute floor at 97 to avoid false certainty
    if score >= 25:
        return "BUY",  confidence
    if score <= -25:
        return "SELL", confidence
    return "HOLD", max(40.0, min(58.0, confidence))


def _levels(price: float, atr: float, action: str):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    # Dynamic ATR multipliers based on ATR-to-price ratio (volatility proxy).
    # High vol → tighter stops to limit $ loss; low vol → wider stops to avoid noise shakeout.
    atr_pct = atr / price if price > 0 else 0.02
    if atr_pct > 0.025:    # high volatility  (ATR > 2.5% of price)
        stop_mult, tgt_mult = 2.0, 2.5
    elif atr_pct < 0.010:  # low volatility   (ATR < 1.0% of price)
        stop_mult, tgt_mult = 3.0, 4.0
    else:                  # normal volatility
        stop_mult, tgt_mult = 2.0, 3.0
    stop   = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult  * atr, 2) if action == "BUY" else round(entry - tgt_mult  * atr, 2)
    risk   = abs(entry - stop)
    reward = abs(target - entry)
    rr     = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


_TIMEFRAME = {
    "intraday": ("within today's session (next few hours)",   "Today"),
    "swing":    ("over the next 2–10 trading days",           "2–10 days"),
    "position": ("over the coming weeks to months",           "Weeks–months"),
}

        # Apply hard empirical ceiling before final assembly
        confidence = min(84.0, confidence)

def _make_plain_english(action: str, ticker: str, style: str, rationale: list,
                         confidence: float, entry, stop, target) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary":    summary,
        "timeframe":  tf_long,
        "tf_short":   tf_short,
        "top_reasons": top,
    }


async def generate_signal(
    ticker: str,
    market_ctx: Optional[dict] = None,
    prefetched_df: Optional[pd.DataFrame] = None,
    prefetched_info: Optional[dict] = None,
) -> Optional[dict]:
    try:
        # Use pre-fetched batch data when available; fall back to individual fetches.
        if prefetched_df is not None:
            df   = prefetched_df
            info = prefetched_info or {}
            news, scraped_news, insider, analyst_recs, earnings_cal, earnings_surp, opt_flow, fundamentals, social, trends, congress, df_1h = await asyncio.gather(
                get_company_news(ticker, days=7),
                get_scraped_news(ticker, (prefetched_info or {}).get("company", ticker), days=7),
                get_insider_activity(ticker, days=30),
                get_analyst_recs(ticker),
                get_earnings_calendar(ticker),
                get_earnings_surprise(ticker),
                get_options_flow(ticker),
                get_fundamentals(ticker),
                get_social_sentiment(ticker),
                get_google_trends(ticker),
                get_congress_signal(ticker),
                get_history(ticker, period="5d", interval="1h"),
            )
            sector_rs = await get_sector_relative_strength(ticker, df)
        else:
            df, info, news, scraped_news, insider, analyst_recs, earnings_cal, earnings_surp, opt_flow, fundamentals, social, trends, congress, df_1h = await asyncio.gather(
                get_history(ticker, period="1y", interval="1d"),
                get_info(ticker),
                get_company_news(ticker, days=7),
                get_scraped_news(ticker, "", days=7),
                get_insider_activity(ticker, days=30),
                get_analyst_recs(ticker),
                get_earnings_calendar(ticker),
                get_earnings_surprise(ticker),
                get_options_flow(ticker),
                get_fundamentals(ticker),
                get_social_sentiment(ticker),
                get_google_trends(ticker),
                get_congress_signal(ticker),
                get_history(ticker, period="5d", interval="1h"),
            )
            sector_rs = await get_sector_relative_strength(ticker, df)

        if df is None or len(df) < 30:
            return None

        tech = calculate_indicators(df)
        if not tech or tech.get("price") is None:
            return None

        # ── Weekly trend (resample daily → weekly, no extra API call) ───────
        weekly_trend = 0  # +1 uptrend, -1 downtrend, 0 neutral
        try:
            weekly = df["Close"].resample("W").last().dropna()
            if len(weekly) >= 20:
                w_sma20 = float(weekly.iloc[-20:].mean())
                w_price = float(weekly.iloc[-1])
                if w_price > w_sma20 * 1.02:
                    weekly_trend = 1
                elif w_price < w_sma20 * 0.98:
                    weekly_trend = -1
        except Exception:
            pass

        price    = tech["price"]
        atr      = tech.get("atr") or price * 0.02
        rsi      = tech.get("rsi")
        hist     = tech.get("macd_hist",      0) or 0
        hist_p   = tech.get("macd_hist_prev", 0) or 0
        sma20    = tech.get("sma20")
        sma50    = tech.get("sma50")
        sma200   = tech.get("sma200")
        bb_upper = tech.get("bb_upper")
        bb_lower = tech.get("bb_lower")
        volume   = tech.get("volume",     0)
        avg_vol  = tech.get("avg_volume", 1) or 1

        score     = 0.0
        rationale = []
        sources   = {"Technical"}
        dominant  = "macd"
        vol_confidence_penalty     = 0.0
        rs_confidence_penalty      = 0.0
        insider_confidence_penalty = 0.0

        # Oscillator group (RSI/Stoch/WR/CCI/MFI): correlated — cap at ±28.
        osc_score = 0.0
        # Moving-average family (SMA200/SMA50/Golden-Death Cross): same underlying
        # price, cap at ±22 to prevent triple-counting "above all MAs" scenarios.
        ma_score = 0.0
        # Trend-continuation family (MACD non-cross / EMA state / ADX): all
        # measure whether the existing trend is strengthening — cap at ±18.
        trend_score = 0.0
        # Volume family (OBV structural trend): cap at ±16.
        volume_score = 0.0

        # ── RSI ────────────────────────────────────────────────────────
        if rsi is not None:
            if rsi < 30:
                osc_score += 20; dominant = "rsi"
                rationale.append({"src": "Technical", "head": "RSI Oversold",
                    "body": f"RSI {rsi:.1f} — deeply oversold. Mean-reversion bounce likely.",
                    "sentiment": "pos", "meta": f"RSI(14) = {rsi:.1f}"})
            elif rsi < 40:
                osc_score += 10
                rationale.append({"src": "Technical", "head": "RSI Weakening",
                    "body": f"RSI {rsi:.1f} — approaching oversold territory.",
                    "sentiment": "pos", "meta": f"RSI(14) = {rsi:.1f}"})
            elif rsi > 70:
                osc_score -= 20; dominant = "rsi"
                rationale.append({"src": "Technical", "head": "RSI Overbought",
                    "body": f"RSI {rsi:.1f} — overbought. Pullback risk elevated.",
                    "sentiment": "neg", "meta": f"RSI(14) = {rsi:.1f}"})
            elif rsi > 60:
                osc_score -= 10
                rationale.append({"src": "Technical", "head": "RSI Elevated",
                    "body": f"RSI {rsi:.1f} — momentum slowing near overbought zone.",
                    "sentiment": "neg", "meta": f"RSI(14) = {rsi:.1f}"})

        # ── Stochastic Oscillator %K/%D ─────────────────────────────────
        stoch_k      = tech.get("stoch_k")
        stoch_d      = tech.get("stoch_d")
        stoch_k_prev = tech.get("stoch_k_prev")
        stoch_d_prev = tech.get("stoch_d_prev")
        if stoch_k is not None and stoch_d is not None:
            stoch_cross_up   = (stoch_k > stoch_d and
                                stoch_k_prev is not None and stoch_d_prev is not None and
                                stoch_k_prev <= stoch_d_prev)
            stoch_cross_down = (stoch_k < stoch_d and
                                stoch_k_prev is not None and stoch_d_prev is not None and
                                stoch_k_prev >= stoch_d_prev)
            if stoch_k < 20 and stoch_cross_up:
                osc_score += 10
                rationale.append({"src": "Technical", "head": "Stochastic Bullish Cross (Oversold)",
                    "body": f"Stochastic %K crossed above %D in oversold zone — high-probability reversal setup.",
                    "sentiment": "pos", "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}"})
            elif stoch_k > 80 and stoch_cross_down:
                osc_score -= 10
                rationale.append({"src": "Technical", "head": "Stochastic Bearish Cross (Overbought)",
                    "body": f"Stochastic %K crossed below %D in overbought zone — momentum rolling over.",
                    "sentiment": "neg", "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}"})
            elif stoch_k < 25:
                osc_score += 5
                rationale.append({"src": "Technical", "head": "Stochastic Oversold",
                    "body": f"Stochastic at {stoch_k:.1f} — price is near recent lows. Bounce potential.",
                    "sentiment": "pos", "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}"})
            elif stoch_k > 75:
                osc_score -= 5
                rationale.append({"src": "Technical", "head": "Stochastic Overbought",
                    "body": f"Stochastic at {stoch_k:.1f} — price is near recent highs. Caution.",
                    "sentiment": "neg", "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}"})

        # ── Williams %R ─────────────────────────────────────────────────
        wr = tech.get("williams_r")
        if wr is not None:
            if wr <= -80:
                osc_score += 6
                rationale.append({"src": "Technical", "head": "Williams %R Oversold",
                    "body": f"Williams %R at {wr:.1f} — price deeply oversold versus 14-day range.",
                    "sentiment": "pos", "meta": f"W%R = {wr:.1f}"})
            elif wr >= -20:
                osc_score -= 6
                rationale.append({"src": "Technical", "head": "Williams %R Overbought",
                    "body": f"Williams %R at {wr:.1f} — price at top of 14-day range. Resistance likely.",
                    "sentiment": "neg", "meta": f"W%R = {wr:.1f}"})

        # ── MACD ───────────────────────────────────────────────────────
        cross_up   = hist > 0 and hist_p <= 0
        cross_down = hist < 0 and hist_p >= 0
        if cross_up:
            score += 22; dominant = "macd"
            rationale.append({"src": "Technical", "head": "MACD Bullish Crossover",
                "body": "MACD crossed above signal line — momentum flipping bullish.",
                "sentiment": "pos", "meta": f"Hist {hist:.5f}"})
        elif cross_down:
            score -= 22; dominant = "macd"
            rationale.append({"src": "Technical", "head": "MACD Bearish Crossover",
                "body": "MACD crossed below signal line — momentum flipping bearish.",
                "sentiment": "neg", "meta": f"Hist {hist:.5f}"})
        elif hist > 0 and hist > hist_p:
            trend_score += 10
            rationale.append({"src": "Technical", "head": "MACD Expanding Bullish",
                "body": "Histogram widening above zero — bullish momentum building.",
                "sentiment": "pos", "meta": f"Hist {hist:.5f}"})
        elif hist < 0 and hist < hist_p:
            trend_score -= 10
            rationale.append({"src": "Technical", "head": "MACD Expanding Bearish",
                "body": "Histogram widening below zero — bearish momentum building.",
                "sentiment": "neg", "meta": f"Hist {hist:.5f}"})

        # ── EMA 8/21 Short-term Momentum ────────────────────────────────
        ema8      = tech.get("ema8")
        ema21     = tech.get("ema21")
        ema8_p    = tech.get("ema8_prev")
        ema21_p   = tech.get("ema21_prev")
        if ema8 and ema21:
            ema_cross_up   = ema8 > ema21 and ema8_p is not None and ema21_p is not None and ema8_p <= ema21_p
            ema_cross_down = ema8 < ema21 and ema8_p is not None and ema21_p is not None and ema8_p >= ema21_p
            if ema_cross_up:
                score += 12
                rationale.append({"src": "Technical", "head": "EMA 8/21 Bullish Cross",
                    "body": "8-EMA crossed above 21-EMA — short-term momentum turning bullish.",
                    "sentiment": "pos", "meta": f"EMA8 ${ema8:.2f} > EMA21 ${ema21:.2f}"})
            elif ema_cross_down:
                score -= 12
                rationale.append({"src": "Technical", "head": "EMA 8/21 Bearish Cross",
                    "body": "8-EMA crossed below 21-EMA — short-term momentum turning bearish.",
                    "sentiment": "neg", "meta": f"EMA8 ${ema8:.2f} < EMA21 ${ema21:.2f}"})
            elif ema8 > ema21:
                trend_score += 5
            else:
                trend_score -= 5

        # ── CCI (Commodity Channel Index) ───────────────────────────────
        cci = tech.get("cci")
        if cci is not None:
            if cci < -150:
                osc_score += 7
                rationale.append({"src": "Technical", "head": "CCI Extreme Oversold",
                    "body": f"CCI at {cci:.0f} — price far below its statistical average. Reversal watch.",
                    "sentiment": "pos", "meta": f"CCI(20) = {cci:.0f}"})
            elif cci < -100:
                osc_score += 3
            elif cci > 150:
                osc_score -= 7
                rationale.append({"src": "Technical", "head": "CCI Extreme Overbought",
                    "body": f"CCI at {cci:.0f} — price far above statistical average. Distribution risk.",
                    "sentiment": "neg", "meta": f"CCI(20) = {cci:.0f}"})
            elif cci > 100:
                osc_score -= 3

        # ── OBV Trend Confirmation ───────────────────────────────────────
        obv_above = tech.get("obv_above")
        obv_slope = tech.get("obv_slope", 0) or 0
        if obv_above is not None:
            if obv_above and obv_slope > 0:
                bonus = 10 if score > 0 else 4
                volume_score += bonus  # OBV → volume family bucket
                rationale.append({"src": "Technical", "head": "OBV Bullish — Volume Accumulation",
                    "body": "On-Balance Volume trending up and above its 20-day MA. Smart money accumulating.",
                    "sentiment": "pos", "meta": f"OBV slope: +{obv_slope:,.0f} shares"})
            elif not obv_above and obv_slope < 0:
                bonus = -10 if score < 0 else -4
                volume_score += bonus  # OBV → volume family bucket
                rationale.append({"src": "Technical", "head": "OBV Bearish — Volume Distribution",
                    "body": "On-Balance Volume trending down and below its 20-day MA. Distribution pressure.",
                    "sentiment": "neg", "meta": f"OBV slope: {obv_slope:,.0f} shares"})

        # ── ADX Trend Strength ───────────────────────────────────────────
        adx      = tech.get("adx")
        plus_di  = tech.get("adx_plus_di")
        minus_di = tech.get("adx_minus_di")
        if adx is not None and plus_di is not None and minus_di is not None:
            if adx > 25:
                if plus_di > minus_di:
                    trend_score += 8  # ADX → trend-continuation family
                    rationale.append({"src": "Technical", "head": f"ADX Strong Uptrend (ADX {adx:.0f})",
                        "body": f"ADX at {adx:.0f} confirms a strong directional uptrend. +DI ({plus_di:.0f}) dominates -DI ({minus_di:.0f}).",
                        "sentiment": "pos", "meta": f"ADX={adx:.0f} +DI={plus_di:.0f} -DI={minus_di:.0f}"})
                else:
                    trend_score -= 8  # ADX → trend-continuation family
                    rationale.append({"src": "Technical", "head": f"ADX Strong Downtrend (ADX {adx:.0f})",
                        "body": f"ADX at {adx:.0f} confirms a strong directional downtrend. -DI ({minus_di:.0f}) dominates +DI ({plus_di:.0f}).",
                        "sentiment": "neg", "meta": f"ADX={adx:.0f} +DI={plus_di:.0f} -DI={minus_di:.0f}"})

        # Apply volume and trend-continuation family caps before MA section.
        # OBV + volume bonus is correlated with CMF and RVOL; ADX/MACD-trend/EMA-state
        # all confirm the same directional trend. Cap each family to prevent over-counting.
        score += max(-16, min(16, volume_score))
        score += max(-18, min(18, trend_score))

        # ── Moving averages — all routed to ma_score family bucket ─────────
        # SMA200, SMA50, and Golden/Death Cross all measure the same thing: "is price
        # above/below its trend averages?" Cap the family at ±22 to prevent a stock
        # that is above all three MAs from getting a 35-point boost from one factor.
        if sma200:
            if price > sma200 * 1.01:
                ma_score += 15; dominant = "sma"
                rationale.append({"src": "Technical", "head": "Above 200-DMA",
                    "body": f"Price ${price:.2f} is {(price/sma200-1)*100:.1f}% above 200-day MA. Long-term uptrend.",
                    "sentiment": "pos", "meta": f"200-DMA ${sma200:.2f}"})
            elif price < sma200 * 0.99:
                ma_score -= 15; dominant = "sma"
                rationale.append({"src": "Technical", "head": "Below 200-DMA",
                    "body": f"Price ${price:.2f} is below the 200-day MA — long-term downtrend.",
                    "sentiment": "neg", "meta": f"200-DMA ${sma200:.2f}"})

        if sma50:
            ma_score += 8 if price > sma50 else -8

        if sma50 and sma200:
            if sma50 > sma200 * 1.005:
                ma_score += 12
                rationale.append({"src": "Technical", "head": "Golden Cross Active",
                    "body": f"50-DMA (${sma50:.0f}) above 200-DMA (${sma200:.0f}). Strong long-term bullish structure.",
                    "sentiment": "pos", "meta": "50-DMA > 200-DMA"})
            elif sma50 < sma200 * 0.995:
                ma_score -= 12
                rationale.append({"src": "Technical", "head": "Death Cross Active",
                    "body": f"50-DMA (${sma50:.0f}) below 200-DMA (${sma200:.0f}). Long-term bearish structure.",
                    "sentiment": "neg", "meta": "50-DMA < 200-DMA"})

        # Apply MA family cap: SMA200 + SMA50 + Golden/Death Cross all correlated
        score += max(-22, min(22, ma_score))

        # ── Bollinger Bands ─────────────────────────────────────────────
        if bb_lower and bb_upper:
            if price <= bb_lower * 1.005:
                score += 10
                rationale.append({"src": "Technical", "head": "Lower Bollinger Band Touch",
                    "body": "Price at lower BB — potential mean-reversion bounce.",
                    "sentiment": "pos", "meta": f"BB Lower ${bb_lower:.2f}"})
            elif price >= bb_upper * 0.995:
                score -= 10
                rationale.append({"src": "Technical", "head": "Upper Bollinger Band Touch",
                    "body": "Price at upper BB — potential overextension.",
                    "sentiment": "neg", "meta": f"BB Upper ${bb_upper:.2f}"})

        # ── 52-Week High / Low Proximity ────────────────────────────────
        wk52_h = tech.get("week52_high")
        wk52_l = tech.get("week52_low")
        if wk52_h and wk52_l and wk52_h > wk52_l:
            pct_from_high = (price - wk52_h) / wk52_h * 100
            pct_from_low  = (price - wk52_l) / wk52_l * 100
            if pct_from_high > -3:
                score += 10
                rationale.append({"src": "Technical", "head": "Near 52-Week High — Breakout Zone",
                    "body": f"Price is within 3% of its 52-week high (${wk52_h:.2f}). Potential breakout; strong momentum.",
                    "sentiment": "pos", "meta": f"52W High ${wk52_h:.2f} | {pct_from_high:.1f}% away"})
            elif pct_from_low < 10:
                score += 8
                rationale.append({"src": "Technical", "head": "Near 52-Week Low — Deep Value Zone",
                    "body": f"Price is within 10% of its 52-week low (${wk52_l:.2f}). Oversold on annual basis.",
                    "sentiment": "pos", "meta": f"52W Low ${wk52_l:.2f} | +{pct_from_low:.1f}% from bottom"})

        # ── Candlestick Pattern ─────────────────────────────────────────
        pattern = tech.get("candle_pattern")
        if pattern == "hammer":
            score += 12
            rationale.append({"src": "Technical", "head": "Hammer Candle — Bullish Reversal",
                "body": "Hammer pattern detected: buyers rejected lower prices, closing near the high. Classic reversal signal.",
                "sentiment": "pos", "meta": "Candlestick: Hammer"})
        elif pattern == "bullish_engulfing":
            score += 12
            rationale.append({"src": "Technical", "head": "Bullish Engulfing Pattern",
                "body": "Today's candle fully engulfs yesterday's bearish candle. Strong buyer conviction.",
                "sentiment": "pos", "meta": "Candlestick: Bullish Engulfing"})
        elif pattern == "shooting_star":
            score -= 12
            rationale.append({"src": "Technical", "head": "Shooting Star — Bearish Reversal",
                "body": "Shooting star detected: sellers rejected higher prices, closing near the low. Distribution signal.",
                "sentiment": "neg", "meta": "Candlestick: Shooting Star"})
        elif pattern == "bearish_engulfing":
            score -= 12
            rationale.append({"src": "Technical", "head": "Bearish Engulfing Pattern",
                "body": "Today's candle fully engulfs yesterday's bullish candle. Strong seller conviction.",
                "sentiment": "neg", "meta": "Candlestick: Bearish Engulfing"})
        elif pattern == "doji":
            # Doji = indecision; only noteworthy in context of a strong prior trend
            if score > 15:
                score -= 5
                rationale.append({"src": "Technical", "head": "Doji — Momentum Stalling",
                    "body": "Doji candle after bullish run. Buyers and sellers at equilibrium — potential reversal.",
                    "sentiment": "neg", "meta": "Candlestick: Doji"})
            elif score < -15:
                score += 5
                rationale.append({"src": "Technical", "head": "Doji — Bearish Momentum Stalling",
                    "body": "Doji candle after bearish run. Potential exhaustion of selling pressure.",
                    "sentiment": "pos", "meta": "Candlestick: Doji"})

        # ── Pivot Point Support / Resistance ────────────────────────────
        pivot    = tech.get("pivot")
        pivot_r1 = tech.get("pivot_r1")
        pivot_s1 = tech.get("pivot_s1")
        if pivot and pivot_r1 and pivot_s1:
            tol = atr * 0.3
            if abs(price - pivot_s1) < tol:
                score += 8
                rationale.append({"src": "Technical", "head": "At Pivot S1 Support",
                    "body": f"Price near classic pivot S1 support (${pivot_s1:.2f}). High-probability bounce level.",
                    "sentiment": "pos", "meta": f"Pivot ${pivot:.2f} | S1 ${pivot_s1:.2f}"})
            elif abs(price - pivot_r1) < tol:
                score -= 8
                rationale.append({"src": "Technical", "head": "At Pivot R1 Resistance",
                    "body": f"Price near classic pivot R1 resistance (${pivot_r1:.2f}). Potential ceiling; watch for rejection.",
                    "sentiment": "neg", "meta": f"Pivot ${pivot:.2f} | R1 ${pivot_r1:.2f}"})

        # ── Volume confirmation ─────────────────────────────────────────
        vol_ratio = volume / avg_vol
        if vol_ratio < 0.80:
            # Low-volume signal — flag for confidence penalty applied at the end
            vol_confidence_penalty = 0.10
            rationale.append({"src": "Technical",
                "head": f"Low Volume — Conviction Reduced ({vol_ratio:.0%} of avg)",
                "body": (f"Today's volume ({volume:,}) is only {vol_ratio:.0%} of the 20-day average. "
                         "Low-volume price moves lack institutional participation and are more "
                         "prone to reversal. Signal confidence reduced."),
                "sentiment": "neg",
                "meta": f"RVOL {vol_ratio:.2f}× | Avg {avg_vol:,}"})
        elif vol_ratio > 1.5:
            bonus = 8 if score >= 0 else -8
            score += bonus
            rationale.append({"src": "Technical", "head": "High-Volume Confirmation",
                "body": f"Volume {vol_ratio:.1f}× 20-day average — conviction behind the move.",
                "sentiment": "pos" if bonus > 0 else "neg",
                "meta": f"Vol {volume:,} | Avg {avg_vol:,}"})

        # ── Short Interest (squeeze potential) ──────────────────────────
        short_float = info.get("short_float_pct")
        short_ratio = info.get("short_ratio")  # days-to-cover
        if short_float is not None:
            dtc_ok = short_ratio is not None and short_ratio > 5
            if short_float > 20 and dtc_ok and score > 5:
                # Classic squeeze setup: both thresholds met — high conviction
                score += 12
                sources.add("Short Interest")
                rationale.append({"src": "Short Interest",
                    "head": f"High-Conviction Squeeze Setup — {short_float:.1f}% Float Short",
                    "body": (f"{short_float:.1f}% of float is sold short with {short_ratio:.1f} days-to-cover. "
                             "Both thresholds confirm a short squeeze setup: any sustained upward move forces "
                             "rapid, mechanically-driven short covering."),
                    "sentiment": "pos",
                    "meta": f"Short Float {short_float:.1f}% | DTC {short_ratio:.1f}d"})
            elif short_float > 20 and score > 5:
                # High float short but low days-to-cover — partial squeeze signal
                score += 7
                sources.add("Short Interest")
                ratio_str = f" Days-to-cover: {short_ratio:.1f}." if short_ratio else ""
                rationale.append({"src": "Short Interest",
                    "head": f"High Short Float {short_float:.1f}% — Squeeze Potential",
                    "body": (f"{short_float:.1f}% of float is sold short.{ratio_str} "
                             "Rising price with heavy short interest can trigger forced short covering."),
                    "sentiment": "pos",
                    "meta": f"Short Float {short_float:.1f}%"})
            elif short_float > 15 and score < -5:
                score -= 5
                sources.add("Short Interest")
                rationale.append({"src": "Short Interest",
                    "head": f"Heavy Short Interest {short_float:.1f}%",
                    "body": f"{short_float:.1f}% of float is short — high institutional conviction in bearish thesis.",
                    "sentiment": "neg", "meta": f"Short Float {short_float:.1f}%"})

        # ── News sentiment (Finnhub + Benzinga/Reuters/Finviz) ─────────────
        # Merge all news sources. Scraped items are labelled by their source
        # (Benzinga, Reuters, Finviz); Finnhub items keep their original label.
        # Dedup on headline words so the same story from two sources counts once.
        avg_sent = 0.0
        _all_news: list[dict] = []
        _seen_ws: list[frozenset] = []

        def _nws(s: str) -> frozenset:
            import re as _re
            return frozenset(w.lower() for w in _re.split(r"\W+", s) if len(w) > 4)

        for _item in list(news or []) + list(scraped_news or []):
            _ws = _nws(_item.get("headline", ""))
            if _ws and not any(len(_ws & _prev) / max(len(_ws), 1) > 0.5 for _prev in _seen_ws):
                _seen_ws.append(_ws)
                _all_news.append(_item)

        if _all_news:
            # Age-decay weight: halves every 24 hours
            total_w, weighted_s = 0.0, 0.0
            for n in _all_news:
                w = 1.0 / (1.0 + n.get("hours_ago", 48) / 24.0)
                weighted_s += n["sentiment"] * w
                total_w    += w
            avg_sent = weighted_s / total_w if total_w > 0 else 0.0

            # Which external sources contributed?
            _src_labels = {n.get("source", "") for n in _all_news}
            if news:
                sources.add("Finnhub")
            for _sl in ("Benzinga", "Reuters", "Finviz"):
                if _sl in _src_labels:
                    sources.add(_sl)

            # Cap news contribution at ±15 — sentiment alone is noisy
            _top = sorted(_all_news, key=lambda x: x.get("hours_ago", 9999))[0]
            _src_lbl = _top.get("source", "News")
            if avg_sent > 0.25:
                score += min(15, round(avg_sent * 22))
                rationale.append({
                    "src":       _src_lbl,
                    "head":      _top["headline"][:90],
                    "body":      _top.get("summary", _top["headline"])[:250],
                    "sentiment": "pos",
                    "meta":      f"{_src_lbl} · {_top.get('hours_ago', '?')}h ago | {len(_all_news)} articles",
                })
            elif avg_sent < -0.25:
                score += max(-15, round(avg_sent * 22))
                rationale.append({
                    "src":       _src_lbl,
                    "head":      _top["headline"][:90],
                    "body":      _top.get("summary", _top["headline"])[:250],
                    "sentiment": "neg",
                    "meta":      f"{_src_lbl} · {_top.get('hours_ago', '?')}h ago | {len(_all_news)} articles",
                })

        # ── SEC EDGAR — insider trades (Form 4) ─────────────────────────
        if insider and insider.get("filings", 0) > 0:
            iscore   = insider["score"]
            score   += iscore
            if abs(iscore) >= 4:
                sources.add("SEC EDGAR")
                net  = insider["net_shares"]
                verb = "Buying" if net > 0 else "Selling"
                rationale.append({
                    "src":       "SEC EDGAR",
                    "head":      f"Insiders {verb} — {insider['filings']} Form 4s (30d)",
                    "body":      (
                        f"{insider['filings']} insider filings in last 30 days. "
                        f"Net: {abs(net):,} shares {'acquired' if net > 0 else 'disposed'}. "
                        f"Buy value ${insider['buy_value']:,.0f} | Sell value ${insider['sell_value']:,.0f}."
                    ),
                    "sentiment": "pos" if iscore > 0 else "neg",
                    "meta":      f"Buys {insider['buys']:,} | Sells {insider['sells']:,}",
                })
            # Confidence-level penalty when insider activity directly contradicts direction
            # (score already penalises the direction; this adds a conviction-level haircut)
            if insider.get("filings", 0) >= 3:
                net       = insider.get("net_shares", 0) or 0
                sell_val  = insider.get("sell_value",  0) or 0
                buy_val   = insider.get("buy_value",   0) or 0
                if score > 0 and net < 0 and sell_val > 250_000:
                    insider_confidence_penalty = 0.10
                elif score < 0 and net > 0 and buy_val > 250_000:
                    insider_confidence_penalty = 0.08

        # ── Liquidity Ceiling (NAAIM > 90%) ─────────────────────────────
        aaii = (market_ctx or {}).get("aaii") or {}
        naaim_exposure = aaii.get("exposure", 50)
        liquidity_ceiling = (naaim_exposure > 90)

        # ── Relative Strength vs S&P 500 ────────────────────────────────
        macro     = (market_ctx or {}).get("macro") or {}
        spy_1m    = macro.get("spy_1m_ret")
        if spy_1m is not None and len(df) >= 21:
            close_arr   = df["Close"].astype(float)
            ticker_1m   = (float(close_arr.iloc[-1]) / float(close_arr.iloc[-21]) - 1) * 100
            rel_strength = round(ticker_1m - spy_1m, 2)
            if rel_strength > 8:
                if not liquidity_ceiling:
                    score += 12
                    sources.add("Relative Strength")
                    rationale.append({"src": "Relative Strength", "head": f"Outperforming S&P 500 by {rel_strength:.1f}%",
                        "body": (f"1-month return: {ticker_1m:+.1f}% vs S&P 500 {spy_1m:+.1f}%. "
                                 f"Relative strength of +{rel_strength:.1f}% signals institutional accumulation."),
                        "sentiment": "pos", "meta": f"1M: {ticker_1m:+.1f}% | SPY: {spy_1m:+.1f}%"})
            elif rel_strength > 2:
                if not liquidity_ceiling:
                    score += 4  # mild outperformance still a positive signal
            elif rel_strength < -8:
                score -= 12
                sources.add("Relative Strength")
                rationale.append({"src": "Relative Strength", "head": f"Underperforming S&P 500 by {abs(rel_strength):.1f}%",
                    "body": (f"1-month return: {ticker_1m:+.1f}% vs S&P 500 {spy_1m:+.1f}%. "
                             f"Persistent underperformance suggests institutional selling or fundamental weakness."),
                    "sentiment": "neg", "meta": f"1M: {ticker_1m:+.1f}% | SPY: {spy_1m:+.1f}%"})
            elif rel_strength < -2:
                score -= 5  # mild underperformance is a negative signal
            # Confidence penalty for BUY signals on SPY underperformers (>2% lag)
            # The score penalty above captures magnitude; this caps conviction separately.
            if rel_strength < -2 and score > 0:
                rs_confidence_penalty = 0.12

        # ── Fear & Greed (market-wide, passed from scanner) ─────────────
        fg = (market_ctx or {}).get("fear_greed")
        if fg:
            bias = fg["score_bias"]
            score += bias
            if abs(bias) >= 7:
                sources.add("Fear&Greed")
                rationale.append({
                    "src":       "Fear & Greed",
                    "head":      f"Market {fg['label']} — F&G {fg['score']:.0f}/100",
                    "body":      (
                        f"CNN Fear & Greed Index at {fg['score']:.0f}/100 ({fg['label']}). "
                        + ("Contrarian signal: extreme fear historically marks bottoms."
                           if bias > 0 else
                           "Contrarian signal: extreme greed historically precedes corrections.")
                    ),
                    "sentiment": fg["sentiment"],
                    "meta":      f"F&G = {fg['score']:.0f} | 1w ago: {fg.get('prev_1w', '?')}",
                })

        # ── Macro context (market-wide, passed from scanner) ────────────
        # Cap at ±8 per ticker so macro can't single-handedly push a weak
        # signal to BUY/SELL (raw macro score can reach ±25 in strong regimes).
        if macro and macro.get("macro_score"):
            m_score = macro["macro_score"]
            m_rationale = list(macro.get("rationale", []))
            
            if liquidity_ceiling:
                for item in list(m_rationale):
                    if "Copper/Gold" in item.get("head", "") and item.get("sentiment") == "pos":
                        m_score -= 6
                        m_rationale.remove(item)

            macro_contrib = max(-8, min(8, m_score))
            score += macro_contrib
            for item in m_rationale:
                rationale.append(item)
                sources.add("Macro")

        # ── ROC(10) Momentum ────────────────────────────────────────────
        roc10 = tech.get("roc10")
        if roc10 is not None:
            if roc10 > 8:
                score += 8
                rationale.append({"src": "Technical", "head": f"Strong Price Momentum +{roc10:.1f}% (10d)",
                    "body": f"Price is up {roc10:.1f}% over the last 10 sessions. Momentum traders will follow.",
                    "sentiment": "pos", "meta": f"ROC(10) = +{roc10:.1f}%"})
            elif roc10 < -8:
                score -= 8
                rationale.append({"src": "Technical", "head": f"Negative Price Momentum {roc10:.1f}% (10d)",
                    "body": f"Price is down {abs(roc10):.1f}% over the last 10 sessions. Selling pressure persists.",
                    "sentiment": "neg", "meta": f"ROC(10) = {roc10:.1f}%"})
            elif roc10 > 4:
                score += 4
            elif roc10 < -4:
                score -= 4

        # ── RSI Divergence ───────────────────────────────────────────────
        rsi_div = tech.get("rsi_divergence")
        if rsi_div == "bullish":
            score += 15; dominant = "rsi"
            rationale.append({"src": "Technical", "head": "Bullish RSI Divergence",
                "body": "Price made a lower low but RSI made a higher low — momentum is recovering while price dips. Classic reversal warning.",
                "sentiment": "pos", "meta": "RSI divergence: bullish"})
        elif rsi_div == "bearish":
            score -= 15; dominant = "rsi"
            rationale.append({"src": "Technical", "head": "Bearish RSI Divergence",
                "body": "Price made a higher high but RSI made a lower high — momentum is fading while price rises. Classic exhaustion signal.",
                "sentiment": "neg", "meta": "RSI divergence: bearish"})

        # ── MACD Zero-Line Cross ─────────────────────────────────────────
        if tech.get("macd_zero_cross_up"):
            score += 10
            rationale.append({"src": "Technical", "head": "MACD Crossed Zero — Trend Flipping Bullish",
                "body": "MACD just crossed above zero. The underlying trend has shifted from bearish to bullish — stronger than a signal-line cross alone.",
                "sentiment": "pos", "meta": f"MACD = {tech.get('macd', 0):.5f}"})
        elif tech.get("macd_zero_cross_down"):
            score -= 10
            rationale.append({"src": "Technical", "head": "MACD Crossed Zero — Trend Flipping Bearish",
                "body": "MACD just crossed below zero. The underlying trend has shifted from bullish to bearish — stronger than a signal-line cross alone.",
                "sentiment": "neg", "meta": f"MACD = {tech.get('macd', 0):.5f}"})

        # ── Z-Score Mean Reversion ───────────────────────────────────────
        zscore = tech.get("zscore")
        if zscore is not None:
            if zscore < -2.5:
                score += 14
                rationale.append({"src": "Technical", "head": f"Z-Score Extreme Oversold ({zscore:.1f}σ)",
                    "body": f"Price is {abs(zscore):.1f} standard deviations below its 20-day average — statistically rare. Strong mean-reversion setup.",
                    "sentiment": "pos", "meta": f"Z-Score = {zscore:.2f}σ"})
            elif zscore < -2.0:
                score += 8
                rationale.append({"src": "Technical", "head": f"Z-Score Oversold ({zscore:.1f}σ)",
                    "body": f"Price {abs(zscore):.1f}σ below 20-day mean. Statistically stretched to the downside.",
                    "sentiment": "pos", "meta": f"Z-Score = {zscore:.2f}σ"})
            elif zscore > 2.5:
                score -= 14
                rationale.append({"src": "Technical", "head": f"Z-Score Extreme Overbought (+{zscore:.1f}σ)",
                    "body": f"Price is {zscore:.1f} standard deviations above its 20-day average — statistically rare. Mean-reversion risk is high.",
                    "sentiment": "neg", "meta": f"Z-Score = +{zscore:.2f}σ"})
            elif zscore > 2.0:
                score -= 8
                rationale.append({"src": "Technical", "head": f"Z-Score Overbought (+{zscore:.1f}σ)",
                    "body": f"Price {zscore:.1f}σ above 20-day mean. Statistically stretched to the upside.",
                    "sentiment": "neg", "meta": f"Z-Score = +{zscore:.2f}σ"})

        # ── Money Flow Index MFI(14) — volume-weighted RSI ───────────────
        mfi = tech.get("mfi")
        if mfi is not None:
            if mfi < 20:
                osc_score += 8
                rationale.append({"src": "Technical", "head": f"MFI Oversold ({mfi:.0f})",
                    "body": f"Money Flow Index at {mfi:.0f} — money is flowing OUT heavily. Volume-confirmed oversold condition. Bounce setup.",
                    "sentiment": "pos", "meta": f"MFI(14) = {mfi:.1f}"})
            elif mfi < 30:
                osc_score += 4
            elif mfi > 80:
                osc_score -= 8
                rationale.append({"src": "Technical", "head": f"MFI Overbought ({mfi:.0f})",
                    "body": f"Money Flow Index at {mfi:.0f} — money is flowing IN excessively. Volume-confirmed overbought condition. Distribution risk.",
                    "sentiment": "neg", "meta": f"MFI(14) = {mfi:.1f}"})
            elif mfi > 70:
                osc_score -= 4

        # Apply oscillator group cap: max ±28 to prevent correlated over-counting
        score += max(-28.0, min(28.0, osc_score))

        # ── Bollinger Band Squeeze + %B ──────────────────────────────────
        bb_squeeze = tech.get("bb_squeeze", False)
        bb_pct_b   = tech.get("bb_pct_b")
        if bb_squeeze and bb_pct_b is not None:
            if bb_pct_b > 0.5:
                score += 8
                rationale.append({"src": "Technical", "head": "Bollinger Squeeze — Upside Breakout Setup",
                    "body": "Bollinger Bands are at their tightest in 20 days (low volatility). Price sits in the upper half — compression before expansion, likely upward.",
                    "sentiment": "pos", "meta": f"BB%B = {bb_pct_b:.2f} | Squeeze ON"})
            else:
                score -= 8
                rationale.append({"src": "Technical", "head": "Bollinger Squeeze — Downside Breakout Risk",
                    "body": "Bollinger Bands at 20-day minimum width. Price in lower half — volatility compression before a likely breakdown.",
                    "sentiment": "neg", "meta": f"BB%B = {bb_pct_b:.2f} | Squeeze ON"})
        elif bb_pct_b is not None:
            if bb_pct_b < 0.05:
                score += 5
            elif bb_pct_b > 0.95:
                score -= 5

        # ── Keltner Channels(20, 2×ATR) ──────────────────────────────────────
        kc_upper = tech.get("kc_upper")
        kc_lower = tech.get("kc_lower")
        if kc_upper and kc_lower:
            sources.add("Technical")
            if price > kc_upper:
                score += 8
                rationale.append({"src": "Technical",
                    "head": f"Keltner Channel Breakout (${kc_upper:.2f})",
                    "body": (f"Price ${price:.2f} broke above the upper Keltner Channel "
                             f"(${kc_upper:.2f}). ATR-based channels filter noise better than "
                             "Bollinger — a KC breakout signals genuine momentum, not just volatility expansion."),
                    "sentiment": "pos", "meta": f"KC Upper: ${kc_upper:.2f}"})
            elif price < kc_lower:
                score -= 8
                rationale.append({"src": "Technical",
                    "head": f"Keltner Channel Breakdown (${kc_lower:.2f})",
                    "body": (f"Price ${price:.2f} fell below the lower Keltner Channel "
                             f"(${kc_lower:.2f}). KC breakdowns are high-conviction distribution signals."),
                    "sentiment": "neg", "meta": f"KC Lower: ${kc_lower:.2f}"})
            # Bollinger Bands entirely inside KC = maximum volatility squeeze
            if bb_upper and bb_lower and bb_upper < kc_upper and bb_lower > kc_lower:
                squeeze_sentiment = "pos" if score > 0 else "neg"
                score += 4 if score > 0 else -4
                rationale.append({"src": "Technical",
                    "head": "Keltner–Bollinger Squeeze — Maximum Coil",
                    "body": ("Bollinger Bands are fully contained within Keltner Channels — "
                             "the tightest possible volatility compression. Historically this precedes "
                             "explosive directional moves. The breakout direction is likely set."),
                    "sentiment": squeeze_sentiment,
                    "meta": f"BB inside KC | KC: ${kc_lower:.2f}–${kc_upper:.2f}"})

        # ── Consecutive Close Streak vs SMA20 ────────────────────────────
        streak = tech.get("close_streak", 0)
        if streak >= 7:
            score += 8
            rationale.append({"src": "Technical", "head": f"{streak} Straight Closes Above SMA20",
                "body": f"Price has closed above its 20-day average for {streak} consecutive sessions. Persistent institutional buying.",
                "sentiment": "pos", "meta": f"Streak: {streak} days above SMA20"})
        elif streak <= -7:
            score -= 8
            rationale.append({"src": "Technical", "head": f"{abs(streak)} Straight Closes Below SMA20",
                "body": f"Price has closed below its 20-day average for {abs(streak)} straight sessions. Sustained distribution.",
                "sentiment": "neg", "meta": f"Streak: {abs(streak)} days below SMA20"})
        elif streak >= 4:
            score += 4
        elif streak <= -4:
            score -= 4

        # ── Credit Stress (HYG trend from macro context) ─────────────────
        hyg_1m = macro.get("hyg_1m_ret")
        if hyg_1m is not None:
            if hyg_1m < -3:
                score -= 8
                sources.add("Macro")
                rationale.append({"src": "Macro", "head": f"Credit Stress: HYG Down {hyg_1m:.1f}% (1M)",
                    "body": "High-yield bonds are falling — a sign of rising credit stress. Risk assets (stocks) tend to follow bonds lower when credit deteriorates.",
                    "sentiment": "neg", "meta": f"HYG 1M = {hyg_1m:.1f}%"})
            elif hyg_1m > 2:
                score += 5
                sources.add("Macro")
                rationale.append({"src": "Macro", "head": f"Credit Healthy: HYG Up {hyg_1m:.1f}% (1M)",
                    "body": "High-yield bonds rising — credit markets are healthy. Risk-on environment favours equities.",
                    "sentiment": "pos", "meta": f"HYG 1M = {hyg_1m:.1f}%"})

        # ── Earnings Proximity Risk ──────────────────────────────────────
        days_to_earnings = earnings_cal.get("days_to_earnings")
        edate = earnings_cal.get("next_earnings_date", "")
        if days_to_earnings is not None and days_to_earnings >= 0:
            sources.add("Earnings")
            if days_to_earnings <= 2:
                # Hard blackout: binary event risk overrides ALL technical signals.
                # IV typically spikes 20–50% into earnings — directional analysis fails.
                score = 0
                sources.add("Risk Gate")
                rationale.append({"src": "Risk Gate",
                    "head": f"Earnings Blackout — {days_to_earnings}d to Binary Event ({edate})",
                    "body": (
                        f"Earnings report in {days_to_earnings} day(s) ({edate}). "
                        "All directional signals are hard-blocked: options implied volatility "
                        "spikes 20–50% ahead of earnings, making price targets statistically "
                        "unreliable. Signal forced to HOLD — reassess after the print."
                    ),
                    "sentiment": "neg", "meta": f"BLACKOUT: earnings {edate}"})
            elif days_to_earnings <= 5:
                score *= 0.75
                rationale.append({"src": "Earnings",
                    "head": f"Earnings in {days_to_earnings}d — Elevated Event Risk",
                    "body": (f"Earnings report in {days_to_earnings} days ({edate}). "
                             "IV expansion ahead of earnings makes directional options trades expensive."),
                    "sentiment": "neg", "meta": f"Next earnings: {edate}"})
            elif days_to_earnings <= 7:
                score *= 0.87
                rationale.append({"src": "Earnings",
                    "head": f"Earnings in {days_to_earnings}d — Early Caution",
                    "body": (f"Earnings report in {days_to_earnings} days ({edate}). "
                             "Stocks often coil or whipsaw in the week before earnings as positioning builds."),
                    "sentiment": "neg", "meta": f"Next earnings: {edate}"})
            elif days_to_earnings <= 14:
                score *= 0.95
                rationale.append({"src": "Earnings",
                    "head": f"Earnings in {days_to_earnings}d — Awareness",
                    "body": (f"Earnings report in {days_to_earnings} days ({edate}). "
                             "Begin tracking IV expansion and analyst estimate revisions."),
                    "sentiment": "neg", "meta": f"Next earnings: {edate}"})

        # ── Earnings Surprise History ─────────────────────────────────────
        consec_beats    = earnings_surp.get("consec_beats", 0)
        misses_4q       = earnings_surp.get("misses_last_4q", 0)
        avg_surp_pct    = earnings_surp.get("avg_surprise_pct")
        last_surp_pct   = earnings_surp.get("last_surprise_pct")
        if earnings_surp:
            sources.add("Earnings")
            if consec_beats >= 4:
                mag_bonus = min(5, round(avg_surp_pct / 5)) if avg_surp_pct and avg_surp_pct > 0 else 0
                score += 10 + mag_bonus
                surp_str = f" avg beat magnitude: +{avg_surp_pct:.1f}%." if avg_surp_pct else ""
                rationale.append({"src": "Earnings",
                    "head": f"{consec_beats} Consecutive EPS Beats",
                    "body": f"Company has beaten analyst EPS estimates for {consec_beats} consecutive quarters.{surp_str} Management consistently delivers positive surprises — strong execution.",
                    "sentiment": "pos",
                    "meta": f"Consec. beats: {consec_beats}" + (f" | Avg beat: +{avg_surp_pct:.1f}%" if avg_surp_pct else "")})
            elif consec_beats >= 2:
                score += 5
                surp_str = f" Last quarter beat by +{last_surp_pct:.1f}%." if last_surp_pct and last_surp_pct > 0 else ""
                rationale.append({"src": "Earnings",
                    "head": f"{consec_beats} Consecutive EPS Beats",
                    "body": f"Company beat EPS estimates in the last {consec_beats} quarters.{surp_str}",
                    "sentiment": "pos",
                    "meta": f"Consec. beats: {consec_beats}"})
            elif misses_4q >= 3:
                mag_penalty = min(4, round(abs(avg_surp_pct) / 5)) if avg_surp_pct and avg_surp_pct < 0 else 0
                score -= 8 + mag_penalty
                surp_str = f" avg miss magnitude: {avg_surp_pct:.1f}%." if avg_surp_pct else ""
                rationale.append({"src": "Earnings",
                    "head": f"Repeated EPS Misses ({misses_4q}/4 Quarters)",
                    "body": f"Company missed analyst EPS estimates in {misses_4q} of the last 4 quarters.{surp_str} Guidance and execution are unreliable.",
                    "sentiment": "neg",
                    "meta": f"Misses: {misses_4q} of last 4Q"})

        # ── Sector Relative Strength ──────────────────────────────────────
        if sector_rs:
            rs  = sector_rs["rs_vs_sector"]
            etf = sector_rs["sector_etf"]
            sources.add("Sector RS")
            if rs > 8:
                score += 10
                rationale.append({"src": "Sector RS",
                    "head": f"Leading {etf} Sector by +{rs:.1f}%",
                    "body": (f"1-month return is {rs:.1f}% above its {etf} sector ETF. "
                             "Outperforming sector peers signals stock-specific institutional demand."),
                    "sentiment": "pos",
                    "meta": f"RS vs {etf}: +{rs:.1f}% | Sector 1M: {sector_rs['sector_1m_ret']:+.1f}%"})
            elif rs > 4:
                score += 5
            elif rs < -8:
                score -= 10
                rationale.append({"src": "Sector RS",
                    "head": f"Lagging {etf} Sector by {abs(rs):.1f}%",
                    "body": (f"1-month return is {abs(rs):.1f}% below its {etf} sector ETF. "
                             "Stock is a sector laggard — possible company-specific weakness."),
                    "sentiment": "neg",
                    "meta": f"RS vs {etf}: {rs:.1f}% | Sector 1M: {sector_rs['sector_1m_ret']:+.1f}%"})
            elif rs < -4:
                score -= 5

            # Sector RS filter: "strong stock in dying sector" trap.
            # A stock outperforming its sector while the sector itself lags SPY is a
            # false leader — the sector tide is falling and will drag it down.
            sector_1m  = sector_rs.get("sector_1m_ret", 0) or 0
            spy_1m_ref = macro.get("spy_1m_ret") or 0
            sector_lag = spy_1m_ref - sector_1m  # positive = sector underperforming SPY
            if score > 0 and rs > 4 and sector_lag > 5:
                score *= 0.82  # ~-18% penalty on BUY conviction
                sources.add("Sector RS")
                rationale.append({"src": "Sector RS",
                    "head": f"Sector Trap Warning — {etf} Lagging SPY by {sector_lag:.1f}%",
                    "body": (f"{ticker} leads its {etf} sector by +{rs:.1f}% but the {etf} sector "
                             f"itself trails SPY by {sector_lag:.1f}%. A strong stock in a "
                             "deteriorating sector is a common trap — the sector tide eventually drags leaders down."),
                    "sentiment": "neg",
                    "meta": f"{etf}: {sector_1m:+.1f}% | SPY: {spy_1m_ref:+.1f}% | Gap: -{sector_lag:.1f}%"})

        # ── Analyst Price Target (yfinance info) ─────────────────────────
        target_mean   = info.get("target_mean")
        analyst_count = info.get("analyst_count") or 0
        if target_mean and analyst_count >= 3 and price > 0:
            upside = (target_mean - price) / price * 100
            target_high = info.get("target_high")
            target_low  = info.get("target_low")
            sources.add("Analyst")
            if upside > 20:
                score += 15
                rationale.append({"src": "Analyst", "head": f"Analysts See {upside:.0f}% Upside",
                    "body": (f"{analyst_count} analysts set a consensus price target of ${target_mean:.2f} "
                             f"vs current ${price:.2f} — {upside:.1f}% implied upside."
                             + (f" High: ${target_high:.2f} | Low: ${target_low:.2f}." if target_high and target_low else "")),
                    "sentiment": "pos", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})
            elif upside > 10:
                score += 8
                rationale.append({"src": "Analyst", "head": f"Analysts See {upside:.0f}% Upside",
                    "body": (f"Consensus target ${target_mean:.2f} implies {upside:.1f}% upside from ${price:.2f} "
                             f"across {analyst_count} analysts."),
                    "sentiment": "pos", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})
            elif upside < -15:
                score -= 12
                rationale.append({"src": "Analyst", "head": f"Analysts See {abs(upside):.0f}% Downside",
                    "body": (f"Consensus target ${target_mean:.2f} is {abs(upside):.1f}% below current price ${price:.2f}. "
                             f"{analyst_count} analysts collectively see limited upside."),
                    "sentiment": "neg", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})
            elif upside < -5:
                score -= 6
                rationale.append({"src": "Analyst", "head": f"Analyst Target Below Market Price",
                    "body": (f"Consensus target ${target_mean:.2f} is {abs(upside):.1f}% below ${price:.2f}. "
                             f"Street expects limited near-term upside."),
                    "sentiment": "neg", "meta": f"Target ${target_mean:.2f} | {analyst_count} analysts"})

        # ── Analyst Recommendation Consensus (yfinance info) ─────────────
        rec_key  = info.get("rec_key", "")
        rec_mean = info.get("rec_mean")
        if rec_key:
            sources.add("Analyst")
            if rec_key in ("strong_buy", "strongBuy") or (rec_mean and rec_mean <= 1.5):
                score += 10
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Strong Buy",
                    "body": "Majority of covering analysts have a Strong Buy consensus. Institutional conviction is high.",
                    "sentiment": "pos", "meta": f"Consensus: {rec_key} (score {rec_mean:.1f}/5)" if rec_mean else f"Consensus: {rec_key}"})
            elif rec_key == "buy" or (rec_mean and rec_mean <= 2.2):
                score += 6
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Buy",
                    "body": "Analyst consensus leans towards a Buy rating.",
                    "sentiment": "pos", "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else "")})
            elif rec_key == "sell" or (rec_mean and rec_mean >= 3.8):
                score -= 8
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Sell",
                    "body": "Analyst consensus leans towards a Sell rating. Street is bearish.",
                    "sentiment": "neg", "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else "")})
            elif rec_key in ("strong_sell", "strongSell") or (rec_mean and rec_mean >= 4.5):
                score -= 12
                rationale.append({"src": "Analyst", "head": "Analysts Rate Stock: Strong Sell",
                    "body": "Strong Sell consensus across covering analysts. Institutional conviction is bearish.",
                    "sentiment": "neg", "meta": f"Consensus: {rec_key}" + (f" ({rec_mean:.1f}/5)" if rec_mean else "")})

        # ── Finnhub Analyst Recommendation Trends ────────────────────────
        if analyst_recs:
            sb  = analyst_recs.get("strong_buy",  0)
            b   = analyst_recs.get("buy",         0)
            h   = analyst_recs.get("hold",        0)
            s   = analyst_recs.get("sell",        0)
            ss  = analyst_recs.get("strong_sell", 0)
            total_recs = sb + b + h + s + ss
            if total_recs >= 5:
                sources.add("Analyst")
                bull_pct = (sb + b) / total_recs * 100
                bear_pct = (s + ss) / total_recs * 100
                period   = analyst_recs.get("period", "")
                if bull_pct >= 70:
                    score += 10
                    rationale.append({"src": "Analyst",
                        "head": f"{bull_pct:.0f}% of Analysts are Bullish",
                        "body": (f"Finnhub consensus ({period}): {sb} Strong Buy + {b} Buy out of {total_recs} analysts. "
                                 f"Strong institutional buy-side conviction."),
                        "sentiment": "pos",
                        "meta": f"SB:{sb} B:{b} H:{h} S:{s} SS:{ss}"})
                elif bull_pct >= 55:
                    score += 5
                elif bear_pct >= 60:
                    score -= 8
                    rationale.append({"src": "Analyst",
                        "head": f"{bear_pct:.0f}% of Analysts are Bearish",
                        "body": (f"Finnhub consensus ({period}): {s} Sell + {ss} Strong Sell out of {total_recs} analysts. "
                                 f"Street is broadly negative on this stock."),
                        "sentiment": "neg",
                        "meta": f"SB:{sb} B:{b} H:{h} S:{s} SS:{ss}"})

        # ── VIX regime multiplier ────────────────────────────────────────
        # Applied symmetrically — elevated vol reduces reliability of ALL directional
        # signals; calm vol boosts reliability of ALL directional signals.
        vix = macro.get("vix")
        if vix is not None:
            if vix > 35:
                score *= 0.60
                rationale.append({"src": "Macro", "head": f"VIX Extreme Fear ({vix:.0f}) — Confidence Reduced",
                    "body": f"VIX at {vix:.0f} signals panic-level volatility. Technical patterns break down in these conditions. Reduce position size significantly.",
                    "sentiment": "neg", "meta": f"VIX = {vix:.0f}"})
            elif vix > 25:
                score *= 0.82   # both BUY and SELL less reliable in high vol
                sources.add("Macro")
            elif vix < 15:
                score *= 1.06   # both BUY and SELL more reliable in low-vol trending market

        # ── Options flow (yfinance multi-expiry enhanced sweep detection) ───
        if opt_flow:
            opt_score, opt_rationale = score_options(opt_flow)
            if opt_score != 0:
                score += opt_score
                sources.add("Options")
                rationale.extend(opt_rationale)

        # ── 13F Institutional flow (with QoQ trend) ──────────────────────────
        inst_signals = (market_ctx or {}).get("institutional_signals", {})
        if ticker in inst_signals:
            inst_sig   = inst_signals[ticker]
            inst_score = inst_sig.get("score", 0)
            qoq_trend  = inst_sig.get("qoq_trend", "neutral")
            if inst_score != 0:
                score += inst_score
                sources.add("13F")
                rat = inst_sig.get("rationale", {})
                if rat:
                    rationale.append(rat)
                # Add an extra QoQ-specific rationale item for rising/falling trends
                if qoq_trend == "rising" and inst_score > 0:
                    rationale.append({
                        "src": "13F",
                        "head": "Institutional Conviction Rising — 2+ Consecutive Quarters Buying",
                        "body": (
                            f"Multiple institutional investors have increased their {ticker} position "
                            "for two or more consecutive quarters. Sustained accumulation signals "
                            "growing conviction rather than a one-off position initiation."
                        ),
                        "sentiment": "pos",
                        "meta": "QoQ trend: rising",
                    })
                elif qoq_trend == "falling" and inst_score < 0:
                    rationale.append({
                        "src": "13F",
                        "head": "Institutional Conviction Falling — 2+ Consecutive Quarters Exiting",
                        "body": (
                            f"Institutions have reduced their {ticker} stake for two or more consecutive "
                            "quarters. Sequential selling is an early exit warning — smart money is "
                            "methodically reducing exposure."
                        ),
                        "sentiment": "neg",
                        "meta": "QoQ trend: falling",
                    })

        # ── Cointegration / Pairs Trading ────────────────────────────────────────
        pairs_signals = (market_ctx or {}).get("pairs_signals", {})
        if ticker in pairs_signals:
            ps       = pairs_signals[ticker]
            ps_score = ps.get("score", 0)
            if abs(ps_score) >= 5:
                score += ps_score
                sources.add("Stat Arb")
                pair      = ps.get("pair_ticker", "?")
                zscore    = ps.get("zscore", 0)
                direction = ps.get("direction", "")
                corr      = ps.get("correlation", 0)
                rationale.append({
                    "src":       "Stat Arb",
                    "head":      f"Pairs Divergence vs {pair} — {direction.title()} ({zscore:+.1f}σ)",
                    "body":      (
                        f"{ticker} is {direction} relative to its cointegrated pair {pair} "
                        f"(spread z-score {zscore:+.1f}σ, {corr:.0%} rolling correlation). "
                        "Statistical arbitrage signals of this magnitude mean-revert "
                        "within 5–15 trading days historically."
                    ),
                    "sentiment": "pos" if ps_score > 0 else "neg",
                    "meta":      f"Z-score: {zscore:+.1f}σ | Pair: {pair} | Corr: {corr:.2f}",
                })

        # ── CBOE Put/Call Ratio (contrarian sentiment) ───────────────────────
        pc = (market_ctx or {}).get("put_call")
        if pc and pc.get("bias"):
            bias = pc["bias"]
            score += bias
            if abs(bias) >= 8:
                sources.add("Options")
                signal_txt = "extreme put buying (fear)" if bias > 0 else "extreme call buying (complacency)"
                rationale.append({"src": "Options",
                    "head": f"CBOE P/C Ratio {pc['ratio']} — {signal_txt.split('(')[1].rstrip(')')} signal",
                    "body": (f"CBOE total put/call ratio at {pc['ratio']}. "
                             + ("Ratio >1.15 signals excessive fear — contrarian bullish."
                                if bias > 0 else "Ratio <0.65 signals complacency — contrarian bearish.")),
                    "sentiment": "pos" if bias > 0 else "neg",
                    "meta": f"P/C = {pc['ratio']}"})

        # ── Options Flow Direction Confirmation ──────────────────────────────
        # Directional layer: does the options market flow align with or contradict
        # the current signal? (Separate from market-wide contrarian above.)
        if pc and pc.get("ratio"):
            pc_ratio = float(pc["ratio"])
            if score > 0:  # BUY signal
                if pc_ratio < 0.70:
                    # Calls dominating — options market is directionally bullish, confirms BUY
                    score += 6
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Confirms BUY (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows call volume dominating puts. "
                                 "The options market is directionally bullish — confirming this BUY signal."),
                        "sentiment": "pos", "meta": f"P/C = {pc_ratio:.2f} (calls dominant)"})
                elif pc_ratio > 1.50:
                    # Puts dominating — options market is directionally bearish, contradicts BUY
                    score -= 10
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Contradicts BUY (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows put volume dominating calls. "
                                 "The options market is positioning bearishly — this conflicts with the BUY signal."),
                        "sentiment": "neg", "meta": f"P/C = {pc_ratio:.2f} (puts dominant)"})
            elif score < 0:  # SELL signal
                if pc_ratio > 1.50:
                    # Puts dominating — confirms SELL direction
                    score -= 6
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Confirms SELL (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows heavy put buying. "
                                 "The options market is directionally bearish — confirming this SELL signal."),
                        "sentiment": "neg", "meta": f"P/C = {pc_ratio:.2f} (puts dominant)"})
                elif pc_ratio < 0.70:
                    # Calls dominating — contradicts SELL direction
                    score += 10
                    sources.add("Options")
                    rationale.append({"src": "Options",
                        "head": f"Options Flow Contradicts SELL (P/C {pc_ratio:.2f})",
                        "body": (f"CBOE P/C ratio of {pc_ratio:.2f} shows calls dominating. "
                                 "Options market is bullish — this contradicts the SELL signal."),
                        "sentiment": "pos", "meta": f"P/C = {pc_ratio:.2f} (calls dominant)"})

        # ── Market Breadth (% of S&P 500 basket above SMA50/200) ────────────
        breadth = (market_ctx or {}).get("breadth")
        if breadth and breadth.get("signal") != "neutral" and breadth.get("score"):
            b_score  = breadth["score"]
            pct_200  = breadth["pct_above_200d"]
            pct_50   = breadth["pct_above_50d"]
            score   += b_score
            sources.add("Market Breadth")
            if b_score >= 10:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Broad Market Participation — {pct_200:.0f}% of S&P 500 Above 200-DMA",
                    "body": (f"{pct_200:.0f}% of leading S&P 500 stocks trade above their 200-day average "
                             f"and {pct_50:.0f}% are above their 50-day average. "
                             "Wide participation confirms the uptrend and provides a strong tailwind for long positions."),
                    "sentiment": "pos",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })
            elif b_score >= 5:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Healthy Market Breadth — {pct_200:.0f}% Above 200-DMA",
                    "body": (f"More than half of S&P 500 benchmark stocks trade above their 200-day average. "
                             "Market internals are constructive — the broad trend supports new longs."),
                    "sentiment": "pos",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })
            elif b_score <= -10:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Market Breadth Deteriorating — Only {pct_200:.0f}% Above 200-DMA",
                    "body": (f"Fewer than 1 in 3 S&P 500 stocks trade above their 200-day average "
                             f"({pct_200:.0f}%). Broad market deterioration reduces the probability of "
                             "individual stock gains — favour defensive positioning or reduced exposure."),
                    "sentiment": "neg",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })
            elif b_score <= -5:
                rationale.append({
                    "src":  "Market Breadth",
                    "head": f"Weakening Market Breadth — {pct_200:.0f}% Above 200-DMA",
                    "body": (f"Less than half of S&P 500 benchmark stocks are above their 200-day average. "
                             "Market internals are weakening — be selective with new long entries."),
                    "sentiment": "neg",
                    "meta": f"Breadth: {pct_200:.0f}% >200d | {pct_50:.0f}% >50d",
                })

        # ── Normalise gathered values ────────────────────────────────────────
        social       = social       or {}
        fundamentals = fundamentals or {}

        # ── Ichimoku Cloud ───────────────────────────────────────────────────
        ichi_tenkan    = tech.get("ichi_tenkan")
        ichi_kijun     = tech.get("ichi_kijun")
        ichi_tenkan_p  = tech.get("ichi_tenkan_p")
        ichi_kijun_p   = tech.get("ichi_kijun_p")
        ichi_cloud_top = tech.get("ichi_cloud_top")
        ichi_cloud_bot = tech.get("ichi_cloud_bot")
        ichi_cloud_bull = tech.get("ichi_cloud_bull")
        ichi_chikou    = tech.get("ichi_chikou_above")
        if ichi_tenkan and ichi_kijun:
            sources.add("Technical")
            # Tenkan/Kijun cross
            if (ichi_tenkan_p and ichi_kijun_p and
                    ichi_tenkan_p <= ichi_kijun_p and ichi_tenkan > ichi_kijun):
                score += 10
                rationale.append({"src": "Technical", "head": "Ichimoku Bullish Cross (TK Cross)",
                    "body": "Tenkan-sen crossed above Kijun-sen — a classic Ichimoku buy signal called the 'TK Cross'. Momentum has shifted bullish.",
                    "sentiment": "pos", "meta": f"Tenkan {ichi_tenkan:.2f} > Kijun {ichi_kijun:.2f}"})
            elif (ichi_tenkan_p and ichi_kijun_p and
                    ichi_tenkan_p >= ichi_kijun_p and ichi_tenkan < ichi_kijun):
                score -= 10
                rationale.append({"src": "Technical", "head": "Ichimoku Bearish Cross (Dead Cross)",
                    "body": "Tenkan-sen crossed below Kijun-sen — a classic Ichimoku sell signal. Momentum has shifted bearish.",
                    "sentiment": "neg", "meta": f"Tenkan {ichi_tenkan:.2f} < Kijun {ichi_kijun:.2f}"})
            # Price vs Cloud
            if ichi_cloud_top and ichi_cloud_bot:
                if price > ichi_cloud_top:
                    score += 8
                    rationale.append({"src": "Technical", "head": f"Price Above Ichimoku Cloud (${ichi_cloud_top:.2f})",
                        "body": f"Price is trading above the Kumo cloud — the Ichimoku trend filter is bullish. The cloud acts as strong support at ${ichi_cloud_bot:.2f}–${ichi_cloud_top:.2f}.",
                        "sentiment": "pos", "meta": f"Cloud: {ichi_cloud_bot:.2f}–{ichi_cloud_top:.2f} | {'Green (bullish)' if ichi_cloud_bull else 'Red (bearish)'}"})
                elif price < ichi_cloud_bot:
                    score -= 8
                    rationale.append({"src": "Technical", "head": f"Price Below Ichimoku Cloud (${ichi_cloud_bot:.2f})",
                        "body": f"Price is below the Kumo cloud — the Ichimoku trend filter is bearish. The cloud acts as resistance at ${ichi_cloud_bot:.2f}–${ichi_cloud_top:.2f}.",
                        "sentiment": "neg", "meta": f"Cloud: {ichi_cloud_bot:.2f}–{ichi_cloud_top:.2f}"})
            # Chikou confirmation — symmetric: confirm = ±4, contradict = ∓4
            if ichi_chikou is True:
                score += 4   # Chikou above price 26 bars ago: bullish regardless of current direction
            elif ichi_chikou is False:
                score -= 4   # Chikou below price 26 bars ago: bearish regardless of current direction

        # ── Chaikin Money Flow ───────────────────────────────────────────────
        cmf      = tech.get("cmf")
        cmf_prev = tech.get("cmf_prev")
        change_pct_abs = abs(tech.get("change_pct", 0) or 0)
        if cmf is not None:
            sources.add("Technical")
            if cmf > 0.20:
                # Strong accumulation — boosted weight vs the 0.15 threshold
                score += 10
                rationale.append({"src": "Technical", "head": f"CMF Strong Accumulation ({cmf:+.2f})",
                    "body": (f"CMF at {cmf:+.2f} — heavy institutional accumulation. "
                             "Money flow is well above the +0.1 threshold, confirming sustained smart-money buying."),
                    "sentiment": "pos", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf > 0.15:
                score += 8
                # Stealth accumulation: strong CMF on a flat price = institutional buying quietly
                if change_pct_abs < 0.5:
                    score += 4
                    rationale.append({"src": "Technical", "head": f"CMF Stealth Accumulation ({cmf:+.2f})",
                        "body": (f"CMF at {cmf:+.2f} while price is nearly flat ({tech.get('change_pct', 0):+.2f}%). "
                                 "Institutions are quietly accumulating without moving the price — a very reliable precursor to a breakout."),
                        "sentiment": "pos", "meta": f"CMF(20) = {cmf:+.2f} | Price flat"})
                else:
                    rationale.append({"src": "Technical", "head": f"Chaikin Money Flow Bullish ({cmf:+.2f})",
                        "body": f"CMF at {cmf:+.2f} — sustained accumulation. Money is flowing into this stock on high volume. Institutional buyers are active.",
                        "sentiment": "pos", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf > 0.05:
                score += 4
                # CMF rising (accelerating) is better than stable
                if cmf_prev is not None and cmf > cmf_prev + 0.05:
                    score += 2
            elif cmf < -0.20:
                score -= 10
                rationale.append({"src": "Technical", "head": f"CMF Strong Distribution ({cmf:+.2f})",
                    "body": (f"CMF at {cmf:+.2f} — heavy institutional distribution. "
                             "Persistent outflows at this level signal sustained smart-money selling."),
                    "sentiment": "neg", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf < -0.15:
                score -= 8
                if change_pct_abs < 0.5:
                    score -= 3  # stealth distribution penalty
                    rationale.append({"src": "Technical", "head": f"CMF Stealth Distribution ({cmf:+.2f})",
                        "body": (f"CMF at {cmf:+.2f} while price is nearly flat. "
                                 "Institutions are quietly selling into price stability — bearish divergence."),
                        "sentiment": "neg", "meta": f"CMF(20) = {cmf:+.2f} | Price flat"})
                else:
                    rationale.append({"src": "Technical", "head": f"Chaikin Money Flow Bearish ({cmf:+.2f})",
                        "body": f"CMF at {cmf:+.2f} — sustained distribution. Money is flowing out of this stock. Institutional sellers are dominating.",
                        "sentiment": "neg", "meta": f"CMF(20) = {cmf:+.2f}"})
            elif cmf < -0.05:
                score -= 4
                if cmf_prev is not None and cmf < cmf_prev - 0.05:
                    score -= 2  # CMF accelerating downward

        # ── VWAP Liquidity Filter ────────────────────────────────────────────
        # Rolling 20-day VWAP is the institutional "cost basis" line for the period.
        # Price below VWAP means the average participant is underwater — a structural
        # liquidity headwind for BUY signals (selling pressure from break-even sellers).
        # Exemption: mean-reversion / oversold plays legitimately buy below VWAP.
        vwap_20  = tech.get("vwap_20")
        vwap_pct = tech.get("vwap_pct")  # positive = above VWAP, negative = below
        if vwap_20 is not None and vwap_pct is not None:
            sources.add("Technical")
            is_oversold_play = rsi is not None and rsi < 35  # exempt mean-reversion
            if score > 0 and vwap_pct < -2.0 and not is_oversold_play:
                # BUY signal with price meaningfully below VWAP — liquidity headwind
                penalty = min(12, abs(vwap_pct) * 1.0)  # 1pt per % below, cap 12
                score  -= penalty
                rationale.append({"src": "Technical",
                    "head": f"Price Below 20-Day VWAP ({vwap_pct:+.1f}%) — Liquidity Headwind",
                    "body": (
                        f"Price is {abs(vwap_pct):.1f}% below the 20-day VWAP (${vwap_20:.2f}). "
                        "Participants who bought over the past 20 sessions are on average underwater, "
                        "creating overhead supply as they exit at break-even. "
                        "BUY signals below VWAP have lower win rates unless confirmed by volume expansion."
                    ),
                    "sentiment": "neg",
                    "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)"})
            elif score > 0 and vwap_pct >= 1.0:
                # Price above VWAP: participants are in profit — less overhead supply
                bonus = min(5, vwap_pct * 0.4)
                score += bonus
                rationale.append({"src": "Technical",
                    "head": f"Price Above VWAP ({vwap_pct:+.1f}%) — Institutional Cost Basis Holds",
                    "body": (
                        f"Price is {vwap_pct:.1f}% above the 20-day VWAP (${vwap_20:.2f}). "
                        "The average participant over the last 20 sessions is in profit — "
                        "reduced overhead supply, supportive for continued upside."
                    ),
                    "sentiment": "pos",
                    "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)"})
            elif score < 0 and vwap_pct > 2.0:
                # SELL signal with price above VWAP: participants are in profit, may take it
                score -= min(5, vwap_pct * 0.4)
                rationale.append({"src": "Technical",
                    "head": f"Price Above VWAP — Profit-Taking Risk ({vwap_pct:+.1f}%)",
                    "body": (
                        f"Price is {vwap_pct:.1f}% above the 20-day VWAP. "
                        "Participants are sitting on gains — any weakness can trigger profit-taking cascades, amplifying the SELL signal."
                    ),
                    "sentiment": "neg",
                    "meta": f"Price ${price:.2f} vs VWAP ${vwap_20:.2f} ({vwap_pct:+.1f}%)"})

        # ── Donchian Channel Breakout ────────────────────────────────────────
        dc_high   = tech.get("donchian_high")
        dc_low    = tech.get("donchian_low")
        dc_high_p = tech.get("donchian_high_p")
        dc_low_p  = tech.get("donchian_low_p")
        if dc_high and dc_low and dc_high_p and dc_low_p:
            if price >= dc_high and price > dc_high_p:
                score += 10
                sources.add("Technical")
                rationale.append({"src": "Technical", "head": f"Donchian 20-Day High Breakout (${dc_high:.2f})",
                    "body": f"Price broke out above the 20-day Donchian channel high (${dc_high:.2f}). The original Turtle Trading breakout signal — momentum is accelerating.",
                    "sentiment": "pos", "meta": f"20d High = ${dc_high:.2f}"})
            elif price <= dc_low and price < dc_low_p:
                score -= 10
                sources.add("Technical")
                rationale.append({"src": "Technical", "head": f"Donchian 20-Day Low Breakdown (${dc_low:.2f})",
                    "body": f"Price broke below the 20-day Donchian channel low (${dc_low:.2f}). Classic momentum breakdown — selling pressure is accelerating.",
                    "sentiment": "neg", "meta": f"20d Low = ${dc_low:.2f}"})

        # ── Price Structure (HH/HL or LH/LL) ────────────────────────────────
        ps = tech.get("price_structure")
        if ps == "hh_hl":
            score += 7
            sources.add("Technical")
            rationale.append({"src": "Technical", "head": "Bullish Price Structure — Higher Highs & Higher Lows",
                "body": "Recent swing highs and lows are both ascending — the classic definition of an uptrend. Bias remains long until structure breaks.",
                "sentiment": "pos", "meta": "HH + HL pattern (20-bar)"})
        elif ps == "lh_ll":
            score -= 7
            sources.add("Technical")
            rationale.append({"src": "Technical", "head": "Bearish Price Structure — Lower Highs & Lower Lows",
                "body": "Recent swing highs and lows are both declining — the classic definition of a downtrend. Bias remains short until structure reverses.",
                "sentiment": "neg", "meta": "LH + LL pattern (20-bar)"})

        # ── Gap Analysis ─────────────────────────────────────────────────────
        gap_pct = tech.get("gap_pct")
        if gap_pct is not None and abs(gap_pct) >= 1.5:
            sources.add("Technical")
            if gap_pct >= 2.5:
                score += 8
                rationale.append({"src": "Technical", "head": f"Bullish Gap Up +{gap_pct:.1f}%",
                    "body": f"Today's open gapped {gap_pct:.1f}% above yesterday's close. Gaps of this size reflect strong institutional conviction — unfilled gaps above prior resistance are particularly bullish.",
                    "sentiment": "pos", "meta": f"Gap: +{gap_pct:.1f}%"})
            elif gap_pct <= -2.5:
                score -= 8
                rationale.append({"src": "Technical", "head": f"Bearish Gap Down {gap_pct:.1f}%",
                    "body": f"Today's open gapped {abs(gap_pct):.1f}% below yesterday's close. Downside gaps reflect urgent selling — institutional distribution overnight.",
                    "sentiment": "neg", "meta": f"Gap: {gap_pct:.1f}%"})
            elif 1.5 <= gap_pct < 2.5:
                score += 4
            elif -2.5 < gap_pct <= -1.5:
                score -= 4

        # ── Relative Volume (RVOL) — direction-aware ─────────────────────────
        # High volume on an up day confirms accumulation; on a down day it confirms
        # distribution. Blind positive bias removed.
        rvol = tech.get("rvol")
        change = tech.get("change", 0) or 0
        if rvol is not None and rvol >= 2.0:
            sources.add("Technical")
            if change >= 0:
                score += 5
                rationale.append({"src": "Technical", "head": f"Elevated Volume on Up Day ({rvol:.1f}×)",
                    "body": f"Today's volume is {rvol:.1f}× the 20-day average on a positive price day — institutional accumulation.",
                    "sentiment": "pos", "meta": f"RVOL = {rvol:.1f}×"})
            else:
                score -= 5
                rationale.append({"src": "Technical", "head": f"Elevated Volume on Down Day ({rvol:.1f}×)",
                    "body": f"Today's volume is {rvol:.1f}× the 20-day average on a negative price day — institutional distribution.",
                    "sentiment": "neg", "meta": f"RVOL = {rvol:.1f}×"})

        # ── ADR Compression ──────────────────────────────────────────────────
        if tech.get("adr_compression"):
            adr = tech.get("adr_pct", 0)
            adr_hi = tech.get("adr_6m_high", adr)
            sources.add("Technical")
            rationale.append({"src": "Technical", "head": "Volatility Coiling — ADR% at 6-Month Low",
                "body": f"Average daily range compressed to {adr:.2f}% vs 6-month high of {adr_hi:.2f}%. Volatility compression historically precedes large directional moves. Watch for a Donchian or Bollinger breakout.",
                "sentiment": "neu", "meta": f"ADR = {adr:.2f}% (6M high: {adr_hi:.2f}%)"})

        # ── Supertrend(7, 3) ─────────────────────────────────────────────────
        st_dir      = tech.get("supertrend_dir",      0) or 0
        st_dir_prev = tech.get("supertrend_dir_prev", 0) or 0
        st_val      = tech.get("supertrend_val")
        if st_dir != 0:
            sources.add("Technical")
            flip_to_bull = st_dir == 1  and st_dir_prev == -1
            flip_to_bear = st_dir == -1 and st_dir_prev ==  1
            val_str      = f" ${st_val:.2f}" if st_val else ""
            if flip_to_bull:
                score += 14; dominant = "macd"
                rationale.append({"src": "Technical",
                    "head": "Supertrend Bullish Flip ↑",
                    "body": (f"Supertrend(7,3) just flipped from bearish to bullish. "
                             f"The ATR-based trailing stop{val_str} now acts as dynamic support. "
                             "A fresh Supertrend flip is one of the cleanest momentum-reversal signals."),
                    "sentiment": "pos",
                    "meta": f"Supertrend flipped BULLISH{val_str}"})
            elif flip_to_bear:
                score -= 14; dominant = "macd"
                rationale.append({"src": "Technical",
                    "head": "Supertrend Bearish Flip ↓",
                    "body": (f"Supertrend(7,3) just flipped from bullish to bearish. "
                             f"The trailing stop{val_str} now acts as overhead resistance. "
                             "High-probability reversal with ATR-confirmed downside momentum."),
                    "sentiment": "neg",
                    "meta": f"Supertrend flipped BEARISH{val_str}"})
            elif st_dir == 1:
                score += 6
                rationale.append({"src": "Technical",
                    "head": f"Supertrend Bullish — ATR Support{val_str}",
                    "body": (f"Supertrend(7,3) is in bullish mode. Price is above its ATR-based "
                             f"trailing stop{val_str} — the trend is intact and stop is rising."),
                    "sentiment": "pos",
                    "meta": f"ST bullish{val_str}"})
            elif st_dir == -1:
                score -= 6
                rationale.append({"src": "Technical",
                    "head": f"Supertrend Bearish — ATR Resistance{val_str}",
                    "body": (f"Supertrend(7,3) is in bearish mode. Price is below its ATR-based "
                             f"trailing stop{val_str} — overhead resistance prevents sustained recoveries."),
                    "sentiment": "neg",
                    "meta": f"ST bearish{val_str}"})

        # ── Hurst Exponent — Regime Classification ────────────────────────────
        hurst = tech.get("hurst")
        if hurst is not None:
            sources.add("Technical")
            if hurst > 0.60:
                # Persistent trending regime — trust momentum signals more
                trend_bonus = 5 if score > 0 else -5
                score += trend_bonus
                rationale.append({"src": "Technical",
                    "head": f"Hurst Exponent {hurst:.2f} — Trending Regime",
                    "body": (f"Hurst exponent of {hurst:.2f} > 0.5 confirms persistent price momentum. "
                             "This stock is in a 'trending' state — breakout and momentum signals "
                             "carry higher win rates here than oscillator-based reversals."),
                    "sentiment": "pos" if score > 0 else "neg",
                    "meta": f"Hurst = {hurst:.2f} (>0.6 = strong trend)"})
            elif hurst < 0.40:
                # Anti-persistent mean-reverting regime — moderate strong directional signals
                if abs(score) > 15:
                    score *= 0.87
                rationale.append({"src": "Technical",
                    "head": f"Hurst Exponent {hurst:.2f} — Mean-Reverting Regime",
                    "body": (f"Hurst exponent of {hurst:.2f} < 0.5 indicates anti-persistent "
                             "price behaviour — recent trends are likely to reverse. "
                             "Momentum/breakout signals are suspect; oversold/overbought reversals are more reliable."),
                    "sentiment": "neu",
                    "meta": f"Hurst = {hurst:.2f} (<0.4 = mean-reverting)"})

        # ── Fractal Dimension Index — Donchian & Bollinger regime filter ─────────
        # FDI complements Hurst: while Hurst uses variance scaling, FDI uses the ratio
        # of the total price path length to the period's high-low range. Together they
        # provide two independent regime readings from different mathematical approaches.
        fdi = tech.get("fdi")
        if fdi is not None:
            sources.add("Technical")
            if fdi < 1.25:
                # Low fractal dimension — nearly linear trend; breakouts are reliable
                fdi_bonus = 5 if score > 0 else -5
                score += fdi_bonus
                rationale.append({"src": "Technical",
                    "head": f"FDI {fdi:.2f} — Trending Market (Trust Breakouts)",
                    "body": (f"Fractal Dimension Index of {fdi:.2f} is well below 1.5 — price is "
                             "moving in a linear, directional fashion. Donchian and Bollinger breakout "
                             "signals are more reliable in this low-fractal regime."),
                    "sentiment": "pos" if score > 0 else "neg",
                    "meta": f"FDI = {fdi:.2f} (<1.25 = trending)"})
            elif fdi > 1.45:
                # High fractal dimension — choppy; breakouts are traps
                if abs(score) > 15:
                    score *= 0.88
                rationale.append({"src": "Technical",
                    "head": f"FDI {fdi:.2f} — Choppy Market (Fade Breakouts)",
                    "body": (f"Fractal Dimension Index of {fdi:.2f} indicates fractal, "
                             "non-directional price action. Breakout signals are more likely to fail — "
                             "mean-reversion setups and oscillator signals are preferred."),
                    "sentiment": "neu",
                    "meta": f"FDI = {fdi:.2f} (>1.45 = choppy)"})

        # ── VIX Term Structure (from macro context) ──────────────────────────
        vix_ratio = (market_ctx or {}).get("macro", {}).get("vix_term_ratio") if market_ctx else None
        if vix_ratio is None and market_ctx:
            vix_ratio = (market_ctx.get("macro") or {}).get("vix_term_ratio")

        # ── Yield Curve (from macro context) ────────────────────────────────
        yc_spread = ((market_ctx or {}).get("macro") or {}).get("yc_spread")
        if yc_spread is not None and abs(yc_spread) > 0.5 and yc_spread not in [None]:
            # Already scored in macro.py and passed via macro_score — just add rationale if not yet present
            pass  # macro.py handles the scoring; we just avoid double-counting

        # ── DXY Impact ───────────────────────────────────────────────────────
        dxy_1m = ((market_ctx or {}).get("macro") or {}).get("dxy_1m")
        if dxy_1m is not None and abs(dxy_1m) >= 2.5:
            # DXY impact is sector-conditional
            # Get sector from sector_rs if available
            sector_etf = (sector_rs or {}).get("sector_etf", "")
            sources.add("Macro")
            int_sectors  = {"XLK", "XLV", "XLY", "XLC"}  # multinationals — hurt by strong $
            dom_sectors  = {"XLU", "XLF", "XLRE"}          # domestic — less affected
            comm_sectors = {"XLB", "XLE"}                  # commodities — hurt by strong $
            if dxy_1m > 2.5:  # strengthening dollar
                if sector_etf in int_sectors or sector_etf in comm_sectors:
                    score -= 5
                    rationale.append({"src": "Macro", "head": f"Strong Dollar Headwind (+{dxy_1m:.1f}% DXY)",
                        "body": f"The US Dollar Index rose {dxy_1m:.1f}% over the past month. A stronger dollar reduces overseas revenue and compresses commodity prices — headwind for this sector.",
                        "sentiment": "neg", "meta": f"DXY 1M = +{dxy_1m:.1f}%"})
            elif dxy_1m < -2.5:  # weakening dollar
                if sector_etf in int_sectors or sector_etf in comm_sectors:
                    score += 5
                    rationale.append({"src": "Macro", "head": f"Weak Dollar Tailwind ({dxy_1m:.1f}% DXY)",
                        "body": f"The US Dollar Index fell {abs(dxy_1m):.1f}% over the past month. A weaker dollar boosts overseas earnings when translated back to USD — tailwind for this sector.",
                        "sentiment": "pos", "meta": f"DXY 1M = {dxy_1m:.1f}%"})

        # ── NAAIM Exposure Index (from market context, key="aaii") ───────────
        aaii = (market_ctx or {}).get("aaii")
        if aaii and aaii.get("signal") != "neutral" and aaii.get("score"):
            a_score  = aaii["score"]
            exposure = aaii.get("exposure", 50)
            pct_rank = aaii.get("pct_rank")
            rank_str = f" | 52w pct rank: {pct_rank:.0f}%" if pct_rank is not None else ""
            score   += a_score
            sources.add("Market Sentiment")
            if a_score >= 8:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Managers Extremely Defensive ({exposure:.0f}% Exposed)",
                    "body": (f"Active managers have only {exposure:.0f}% equity exposure — well below average. "
                             "When professionals are this defensive, mean-reversion rallies tend to be sharp as they scramble to cover underexposure."),
                    "sentiment": "pos", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})
            elif a_score >= 4:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Below-Average Equity Exposure ({exposure:.0f}%)",
                    "body": f"Active managers are {exposure:.0f}% exposed to equities — below the historical average (~65%). Defensive positioning leaves room for a buy-in rally.",
                    "sentiment": "pos", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})
            elif a_score <= -8:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Managers Fully Invested ({exposure:.0f}% Exposed)",
                    "body": (f"Active managers are {exposure:.0f}% exposed to equities — near maximum. "
                             "When professionals are this fully invested, there is limited incremental buying power left to drive prices higher."),
                    "sentiment": "neg", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})
            elif a_score <= -4:
                rationale.append({"src": "Market Sentiment",
                    "head": f"NAAIM: Elevated Equity Positioning ({exposure:.0f}%)",
                    "body": f"Active managers are {exposure:.0f}% exposed — above-average positioning. Crowded long positioning reduces the marginal buyer pool.",
                    "sentiment": "neg", "meta": f"NAAIM = {exposure:.1f}%{rank_str}"})

        # ── COT (Commitment of Traders) ──────────────────────────────────────
        cot = (market_ctx or {}).get("cot")
        if cot and cot.get("signal") != "neutral" and cot.get("score"):
            c_score  = cot["score"]
            net_pct  = cot["net_pct"]
            score   += c_score
            sources.add("Market Sentiment")
            if c_score >= 8:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Extremely Short S&P ({net_pct:+.0f}%)",
                    "body": f"CFTC COT report shows leveraged funds are {abs(net_pct):.0f}% net short S&P 500 futures. Historically, when fast money is this short, the market bounces sharply — a classic short-squeeze setup.",
                    "sentiment": "pos", "meta": f"COT net: {net_pct:+.0f}%"})
            elif c_score >= 4:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Net Short S&P ({net_pct:+.0f}%)",
                    "body": f"CFTC COT shows leveraged funds leaning short on S&P 500 futures. Mild contrarian tailwind.",
                    "sentiment": "pos", "meta": f"COT net: {net_pct:+.0f}%"})
            elif c_score <= -8:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Extremely Long S&P ({net_pct:+.0f}%)",
                    "body": f"CFTC COT shows leveraged funds {net_pct:.0f}% net long S&P 500 futures. Crowded long positioning often precedes reversals.",
                    "sentiment": "neg", "meta": f"COT net: {net_pct:+.0f}%"})
            elif c_score <= -4:
                rationale.append({"src": "Market Sentiment", "head": f"COT: Leveraged Funds Net Long S&P ({net_pct:+.0f}%)",
                    "body": f"Leveraged funds are net long S&P futures — mild contrarian warning signal.",
                    "sentiment": "neg", "meta": f"COT net: {net_pct:+.0f}%"})

        # ── Piotroski F-Score ───────────────────────────────────────────────
        f_score = fundamentals.get("piotroski_f")
        if f_score is not None:
            sources.add("Fundamentals")
            if f_score >= 7:
                score += 12
                rationale.append({"src": "Fundamentals", "head": f"Piotroski F-Score {f_score}/9 — Financially Strong",
                    "body": f"Piotroski F-Score of {f_score}/9: company scores strongly across profitability, leverage, and efficiency tests. High-F-score stocks outperform low-F-score stocks by 7–9% annually in academic studies.",
                    "sentiment": "pos", "meta": f"F-Score: {f_score}/9"})
            elif f_score >= 5:
                score += 5
            elif f_score <= 2:
                score -= 10
                rationale.append({"src": "Fundamentals", "head": f"Piotroski F-Score {f_score}/9 — Financially Weak",
                    "body": f"Piotroski F-Score of only {f_score}/9: poor profitability, increasing leverage, and deteriorating efficiency. Low-F-score stocks are academic short candidates.",
                    "sentiment": "neg", "meta": f"F-Score: {f_score}/9"})
            elif f_score <= 4:
                score -= 4

        # ── Free Cash Flow Yield ─────────────────────────────────────────────
        fcf_yield = fundamentals.get("fcf_yield")
        if fcf_yield is not None:
            sources.add("Fundamentals")
            if fcf_yield > 8:
                score += 8
                rationale.append({"src": "Fundamentals", "head": f"Strong FCF Yield {fcf_yield:.1f}%",
                    "body": f"Free cash flow yield of {fcf_yield:.1f}% — substantially above current Treasury rates. The company generates enough cash to fund growth, buybacks, or dividends without new debt.",
                    "sentiment": "pos", "meta": f"FCF Yield: {fcf_yield:.1f}%"})
            elif fcf_yield > 4:
                score += 4
            elif fcf_yield < 0:
                score -= 6
                rationale.append({"src": "Fundamentals", "head": "Negative Free Cash Flow",
                    "body": "Company is burning more cash than it generates from operations. Requires external financing (debt or equity) to fund operations. Higher risk.",
                    "sentiment": "neg", "meta": f"FCF Yield: {fcf_yield:.1f}%"})

        # ── Revenue Growth Acceleration ──────────────────────────────────────
        rev_acc = fundamentals.get("rev_accelerating")
        g1      = fundamentals.get("rev_growth_q1")
        g2      = fundamentals.get("rev_growth_q2")
        if rev_acc is not None and g1 is not None and g2 is not None:
            sources.add("Fundamentals")
            if rev_acc and g1 > 5:
                score += 6
                rationale.append({"src": "Fundamentals", "head": f"Revenue Growth Accelerating (+{g1:.1f}% QoQ)",
                    "body": f"Quarterly revenue growth accelerated from +{g2:.1f}% to +{g1:.1f}% QoQ. Acceleration is the CAN SLIM key metric — expanding revenues at an increasing rate signal a business in breakout mode.",
                    "sentiment": "pos", "meta": f"Rev growth: {g2:.1f}% → {g1:.1f}% QoQ"})
            elif not rev_acc and g1 < -2:
                score -= 5
                rationale.append({"src": "Fundamentals", "head": f"Revenue Growth Decelerating ({g1:.1f}% QoQ)",
                    "body": f"Revenue growth slowed from {g2:.1f}% to {g1:.1f}% QoQ. Decelerating growth often leads to multiple compression as analysts lower estimates.",
                    "sentiment": "neg", "meta": f"Rev growth: {g2:.1f}% → {g1:.1f}% QoQ"})

        # ── ROE Trend ────────────────────────────────────────────────────────
        roe_improving = fundamentals.get("roe_improving")
        roe_now       = fundamentals.get("roe_now")
        roe_prev      = fundamentals.get("roe_prev")
        if roe_improving is not None and roe_now is not None:
            sources.add("Fundamentals")
            if roe_improving and roe_now > 15:
                score += 5
                rationale.append({"src": "Fundamentals", "head": f"ROE Improving — {roe_now:.1f}%",
                    "body": f"Return on equity rose from {roe_prev:.1f}% to {roe_now:.1f}%. Improving ROE above 15% signals a company compounding capital at a healthy rate.",
                    "sentiment": "pos", "meta": f"ROE: {roe_prev:.1f}% → {roe_now:.1f}%"})
            elif not roe_improving and roe_now < roe_prev:
                delta = roe_prev - roe_now
                if delta > 5:
                    score -= 4
                    rationale.append({"src": "Fundamentals", "head": f"ROE Declining — {roe_now:.1f}%",
                        "body": f"Return on equity fell {delta:.1f}pp from {roe_prev:.1f}% to {roe_now:.1f}%. Declining ROE often precedes earnings disappointments.",
                        "sentiment": "neg", "meta": f"ROE: {roe_prev:.1f}% → {roe_now:.1f}%"})

        # ── Dividend Yield vs 10Y Rate ────────────────────────────────────────
        div_yield = fundamentals.get("div_yield_pct")
        t10y_rate = ((market_ctx or {}).get("macro") or {}).get("t10y")
        if div_yield and div_yield > 0 and t10y_rate:
            sources.add("Fundamentals")
            yield_gap = div_yield - t10y_rate
            if yield_gap > 1.0:
                score += 6
                rationale.append({"src": "Fundamentals", "head": f"Dividend Yield {div_yield:.1f}% > 10Y Treasury {t10y_rate:.1f}%",
                    "body": f"Stock yields {div_yield:.1f}% — {yield_gap:.1f}pp above the 10-year Treasury. When a blue chip yields more than risk-free bonds, yield-seeking demand increases.",
                    "sentiment": "pos", "meta": f"Yield gap: +{yield_gap:.1f}pp"})
            elif yield_gap < -2.0:
                score -= 3
                rationale.append({"src": "Fundamentals", "head": f"Bond Alternative More Attractive",
                    "body": f"10Y Treasury ({t10y_rate:.1f}%) significantly exceeds the stock's {div_yield:.1f}% dividend yield by {abs(yield_gap):.1f}pp. Risk-free alternative is compelling.",
                    "sentiment": "neg", "meta": f"Yield gap: {yield_gap:.1f}pp"})

        # ── Buyback Yield ─────────────────────────────────────────────────────
        bb_yield = fundamentals.get("buyback_yield")
        if bb_yield and bb_yield > 3:
            sources.add("Fundamentals")
            score += 4
            rationale.append({"src": "Fundamentals", "head": f"Active Share Buyback — {bb_yield:.1f}% Yield",
                "body": f"Company returned {bb_yield:.1f}% of market cap to shareholders through buybacks. Active repurchases signal management confidence and reduce the float — mechanically bullish.",
                "sentiment": "pos", "meta": f"Buyback yield: {bb_yield:.1f}%"})

        # ── Social Sentiment (StockTwits + Reddit WSB) ───────────────────────
        st_bull_pct = social.get("st_bull_pct")
        wsb_7d      = social.get("wsb_mentions_7d", 0)
        wsb_1d      = social.get("wsb_mentions_1d", 0)
        if st_bull_pct is not None and social.get("st_total", 0) >= 5:
            sources.add("Social")
            if st_bull_pct >= 90:
                # Extreme retail bullishness = contrarian SELL (euphoria top)
                score -= 5
                rationale.append({"src": "Social", "head": f"StockTwits Extreme Bullishness ({st_bull_pct:.0f}%) — Contrarian Bearish",
                    "body": f"{st_bull_pct:.0f}% of StockTwits messages are bullish — near-euphoric retail sentiment. Historically extreme retail bullishness precedes short-term reversals.",
                    "sentiment": "neg", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
            elif st_bull_pct >= 75:
                score += 4
                rationale.append({"src": "Social", "head": f"StockTwits Strongly Bullish ({st_bull_pct:.0f}%)",
                    "body": f"{st_bull_pct:.0f}% of StockTwits messages on ${ticker} are bullish. Elevated retail optimism can create near-term upside momentum.",
                    "sentiment": "pos", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
            elif st_bull_pct <= 10:
                # Extreme retail pessimism = contrarian BUY (capitulation)
                score += 5
                rationale.append({"src": "Social", "head": f"StockTwits Extreme Bearishness ({st_bull_pct:.0f}% bull) — Contrarian Bullish",
                    "body": f"Only {st_bull_pct:.0f}% of StockTwits messages are bullish — near-capitulation retail sentiment. Extreme pessimism often marks near-term bottoms.",
                    "sentiment": "pos", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
            elif st_bull_pct <= 30:
                score += 3
                rationale.append({"src": "Social", "head": f"StockTwits Bearish ({st_bull_pct:.0f}% bull) — Contrarian",
                    "body": f"Only {st_bull_pct:.0f}% of StockTwits messages are bullish. Retail pessimism is a mild contrarian buy indicator.",
                    "sentiment": "pos", "meta": f"ST Bull: {st_bull_pct:.0f}% | {social.get('st_total',0)} messages"})
        if wsb_1d >= 10:
            sources.add("Social")
            score += 4
            rationale.append({"src": "Social", "head": f"Reddit WSB Mention Surge — {wsb_1d} Posts Today",
                "body": f"${ticker} mentioned in {wsb_1d} Reddit WSB posts in the past 24h ({wsb_7d} this week). Rising retail attention can drive short-term volume and volatility.",
                "sentiment": "pos", "meta": f"WSB: {wsb_1d} today | {wsb_7d} this week"})

        # ── Orthogonality Bonus — independent information sets converging ────────
        # Signals from fundamentally uncorrelated sources (different data pipelines,
        # different filing cadences, different market participants) carry greater
        # statistical weight than a second technical indicator reading the same price.
        # Reward convergence across truly independent sources.
        _agree = "pos" if score > 0 else "neg"
        _indep = {
            "13F":       any(r.get("src") == "13F"       and r.get("sentiment") == _agree for r in rationale),
            "Insider":   any(r.get("src") == "SEC EDGAR" and r.get("sentiment") == _agree for r in rationale),
            "Congress":  any(r.get("src") == "Insider"   and r.get("sentiment") == _agree for r in rationale),
            "Piotroski": any("Piotroski" in r.get("head","") and r.get("sentiment") == _agree for r in rationale),
            "Social":    any(r.get("src") == "Social"    and r.get("sentiment") == _agree for r in rationale),
            "Macro":     any(r.get("src") == "Macro"     and r.get("sentiment") == _agree for r in rationale),
        }
        _n_indep = sum(_indep.values())
        if _n_indep >= 2:
            _orth_bonus = _n_indep * 3  # +3 per independent confirming source, up to +18
            score += _orth_bonus if score > 0 else -_orth_bonus
            sources.add("Orthogonalization")
            _indep_names = ", ".join(k for k, v in _indep.items() if v)
            rationale.append({"src": "Orthogonalization",
                "head": f"{_n_indep} Independent Sources Agree — Orthogonal Alpha",
                "body": (f"{_indep_names} all confirm the {'bullish' if _agree == 'pos' else 'bearish'} thesis "
                         "from uncorrelated data pipelines (filings, fundamentals, positioning, macro). "
                         "Each source uses different information — convergence raises statistical confidence."),
                "sentiment": _agree,
                "meta": f"{_n_indep} independent sources: {_indep_names}"})

        # ── Tier 6: Signal Clustering Boost ─────────────────────────────────
        # When ≥6 independent source CATEGORIES all agree with the dominant direction,
        # the conviction is significantly higher than the sum of parts.
        agree_dir = "pos" if score > 0 else "neg"
        source_cats = {
            "TA":      any(r.get("src") == "Technical"        for r in rationale if r.get("sentiment") == agree_dir),
            "OPT":     any(r.get("src") == "Options"          for r in rationale if r.get("sentiment") == agree_dir),
            "INST":    any(r.get("src") == "13F"              for r in rationale if r.get("sentiment") == agree_dir),
            "INSIDE":  any(r.get("src") in ("Insider","SEC EDGAR") for r in rationale if r.get("sentiment") == agree_dir),
            "AN":      any(r.get("src") == "Analyst"          for r in rationale if r.get("sentiment") == agree_dir),
            "MACRO":   any(r.get("src") == "Macro"            for r in rationale if r.get("sentiment") == agree_dir),
            "SENT":    any(r.get("src") in ("Market Sentiment","Fear&Greed","Market Breadth") for r in rationale if r.get("sentiment") == agree_dir),
            "FUND":    any(r.get("src") == "Fundamentals"     for r in rationale if r.get("sentiment") == agree_dir),
            "SOCIAL":  any(r.get("src") == "Social"           for r in rationale if r.get("sentiment") == agree_dir),
            "EARN":    any(r.get("src") == "Earnings"         for r in rationale if r.get("sentiment") == agree_dir),
        }
        agreeing_cats = sum(source_cats.values())
        if agreeing_cats >= 6:
            cluster_boost = round(score * 0.12, 1)  # 12% boost — conviction multiplier
            score += cluster_boost
            sources.add("Signal Cluster")
            rationale.append({"src": "Signal Cluster",
                "head": f"High-Conviction Signal — {agreeing_cats} Independent Categories Agree",
                "body": (f"{agreeing_cats} independent signal categories all point {'bullish' if agree_dir=='pos' else 'bearish'}: "
                         f"{', '.join(k for k,v in source_cats.items() if v)}. "
                         "When this many uncorrelated sources converge, the signal is significantly more reliable."),
                "sentiment": agree_dir,
                "meta": f"{agreeing_cats} source categories converging"})

        # ── Tier 6: Regime-Conditional Weighting ─────────────────────────────
        # Symmetric: penalise counter-trend signals, boost with-trend signals.
        # Bear market: BUY haircut AND SELL boost. Bull market: SELL haircut AND BUY boost.
        sp500_trend = ((market_ctx or {}).get("macro") or {}).get("sp500_trend")
        if sp500_trend == "down":
            if score > 0:   # BUY against the bear trend — less reliable
                score *= 0.82
                rationale.append({"src": "Macro", "head": "Bear Market Regime — Long Signal Discounted",
                    "body": "S&P 500 is below its 50-day average. Counter-trend long signals carry lower win rates. Confidence reduced.",
                    "sentiment": "neg", "meta": "SPX < 50-DMA regime"})
            elif score < 0:  # SELL with the bear trend — more reliable
                score *= 1.10
        elif sp500_trend == "up":
            if score < 0:   # SELL against the bull trend — less reliable
                score *= 0.90
            elif score > 0:  # BUY with the bull trend — more reliable
                score *= 1.05

        # ── Earnings Estimate Revision Momentum ─────────────────────────────
        target_mean   = info.get("target_mean")
        analyst_count = info.get("analyst_count") or 0
        if target_mean and analyst_count >= 3 and price > 0:
            import time as _time_mod
            now_ts = _time_mod.time()
            prev = _analyst_cache.get(ticker, {})
            prev_mean  = prev.get("mean")
            prev_ts    = prev.get("ts", 0)
            prev_count = prev.get("count", analyst_count)
            
            # Invalidate stale cache entries (>1 hour old)
            if prev_ts and (now_ts - prev_ts) > _ANALYST_CACHE_TTL:
                prev_mean = None  # Force refresh
            
            _analyst_cache[ticker] = {"mean": target_mean, "count": analyst_count, "ts": now_ts}
            if prev_mean and prev_mean > 0:
                revision_pct = (target_mean - prev_mean) / prev_mean * 100
                count_grew   = analyst_count > prev_count
                if revision_pct > 5 and count_grew:
                    score += 8
                    sources.add("Analyst")
                    rationale.append({"src": "Analyst",
                        "head": f"Analyst Target Revised Up +{revision_pct:.1f}% — Positive Momentum",
                        "body": (f"Consensus price target upgraded from ${prev_mean:.2f} to ${target_mean:.2f} "
                                 f"(+{revision_pct:.1f}%) as analyst coverage expanded to {analyst_count}. "
                                 "Rising estimates with growing coverage is a strong leading indicator."),
                        "sentiment": "pos",
                        "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f} | Analysts: {analyst_count}"})
                elif revision_pct > 5:
                    score += 5
                    sources.add("Analyst")
                    rationale.append({"src": "Analyst",
                        "head": f"Analyst Target Revised Up +{revision_pct:.1f}%",
                        "body": f"Consensus price target raised from ${prev_mean:.2f} to ${target_mean:.2f}. Positive estimate revision momentum tends to persist.",
                        "sentiment": "pos",
                        "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f}"})
                elif revision_pct < -5:
                    score -= 6
                    sources.add("Analyst")
                    rationale.append({"src": "Analyst",
                        "head": f"Analyst Target Revised Down {revision_pct:.1f}%",
                        "body": (f"Consensus price target cut from ${prev_mean:.2f} to ${target_mean:.2f} "
                                 f"({revision_pct:.1f}%). Negative estimate revisions tend to cluster — where there's one cut, more often follow."),
                        "sentiment": "neg",
                        "meta": f"Target: ${prev_mean:.2f} → ${target_mean:.2f} | Analysts: {analyst_count}"})

        # ── Google Trends ────────────────────────────────────────────────────
        trends = trends or {}
        gt_score  = trends.get("score", 0)
        gt_chg    = trends.get("change_pct")
        gt_recent = trends.get("recent")
        if gt_score != 0 and gt_chg is not None:
            score += gt_score
            sources.add("Social")
            if gt_score > 0:
                rationale.append({"src": "Social",
                    "head": f"Google Search Surge +{gt_chg:.0f}% — Retail FOMO Building",
                    "body": (f"Search volume for '{ticker} stock' jumped {gt_chg:.0f}% vs prior 4-week average "
                             f"(index: {gt_recent:.0f}/100). Rising retail attention typically precedes "
                             "near-term price momentum as new buyers enter the market."),
                    "sentiment": "pos",
                    "meta": f"Trends: +{gt_chg:.0f}% vs 4w avg | Score: {gt_recent:.0f}/100"})
            elif gt_score < 0:
                rationale.append({"src": "Social",
                    "head": f"Google Search Collapse {gt_chg:.0f}% — Retail Interest Fading",
                    "body": f"Search interest for '{ticker} stock' dropped {abs(gt_chg):.0f}% vs prior 4 weeks. Fading retail attention reduces the marginal buyer pool.",
                    "sentiment": "neg",
                    "meta": f"Trends: {gt_chg:.0f}% vs 4w avg"})

        # ── Congressional Trading (Quiverquant) ──────────────────────────────
        congress = congress or {}
        cg_score = congress.get("score", 0)
        cg_buys  = congress.get("buys", 0)
        cg_sells = congress.get("sells", 0)
        cg_net   = congress.get("net", 0)
        if cg_score != 0:
            score += cg_score
            sources.add("Insider")
            if cg_score > 0:
                recent_reps = ", ".join(b["rep"] for b in congress.get("recent_buys", [])[:2])
                rationale.append({"src": "Insider",
                    "head": f"Congressional Buying — {cg_buys} Purchase{'s' if cg_buys>1 else ''} (90d)",
                    "body": (f"{cg_buys} congressional purchase{'s' if cg_buys>1 else ''} vs {cg_sells} sale{'s' if cg_sells!=1 else ''} in the past 90 days. "
                             + (f"Buyers include: {recent_reps}. " if recent_reps else "")
                             + "Senators and representatives historically outperform the market by 6–12% annually."),
                    "sentiment": "pos",
                    "meta": f"Congress: {cg_buys} buys, {cg_sells} sells (90d)"})
            elif cg_score < 0:
                rationale.append({"src": "Insider",
                    "head": f"Congressional Selling — {cg_sells} Sale{'s' if cg_sells>1 else ''} (90d)",
                    "body": f"{cg_sells} congressional sale{'s' if cg_sells!=1 else ''} vs {cg_buys} purchase{'s' if cg_buys!=1 else ''} in the past 90 days. Net selling by politicians — who often have policy insight — is a caution flag.",
                    "sentiment": "neg",
                    "meta": f"Congress: {cg_buys} buys, {cg_sells} sells (90d)"})

        # ── Sector Rotation Bias ──────────────────────────────────────────────
        rotation = ((market_ctx or {}).get("macro") or {}).get("sector_rotation")
        if rotation and rotation.get("stage") and sector_rs:
            sector_etf = sector_rs.get("sector_etf", "")
            stage      = rotation["stage"]
            favoured   = rotation.get("favoured", [])
            avoid      = rotation.get("avoid", [])
            conf       = rotation.get("confidence", 0)
            if sector_etf and conf >= 50:
                sources.add("Macro")
                if sector_etf in favoured:
                    score += 6
                    rationale.append({"src": "Macro",
                        "head": f"Sector Rotation Tailwind — {sector_etf} Favoured in {stage.title()} Cycle",
                        "body": (f"Current macro indicators (yield curve, VIX, credit spreads, S&P trend) suggest a "
                                 f"'{stage}' economic cycle stage. {sector_etf} historically outperforms in this environment. "
                                 f"Sector rotation model confidence: {conf}%."),
                        "sentiment": "pos",
                        "meta": f"Cycle: {stage} | Favoured: {', '.join(favoured[:3])}"})
                elif sector_etf in avoid:
                    score -= 5
                    rationale.append({"src": "Macro",
                        "head": f"Sector Rotation Headwind — {sector_etf} Underperforms in {stage.title()} Cycle",
                        "body": (f"The '{stage}' cycle stage typically sees {sector_etf} underperform. "
                                 f"Capital tends to rotate toward: {', '.join(favoured[:3])}. "
                                 f"Model confidence: {conf}%."),
                        "sentiment": "neg",
                        "meta": f"Cycle: {stage} | Avoid: {', '.join(avoid[:3])}"})

        # ── Multi-timeframe confirmation (weekly + 1H) ───────────────────────
        # Weekly trend
        if weekly_trend == 1 and score > 0:
            score *= 1.10  # daily BUY confirmed by weekly uptrend
        elif weekly_trend == -1 and score > 0:
            score *= 0.70  # daily BUY against weekly downtrend
            rationale.append({"src": "Technical", "head": "Weekly Downtrend Conflict",
                "body": "Daily BUY signal contradicts the weekly downtrend. Price is below its 20-week average — counter-trend trades have lower win rates.",
                "sentiment": "neg", "meta": "Weekly SMA20 bearish"})
        elif weekly_trend == -1 and score < 0:
            score *= 1.10  # daily SELL confirmed by weekly downtrend
        elif weekly_trend == 1 and score < 0:
            score *= 0.75  # daily SELL against weekly uptrend

        # 1H intraday timeframe confirmation — completes the 1D/1W/1H trifecta.
        # Requires RSI, MACD, and EMA all aligned on the 1H chart.
        try:
            if df_1h is not None and len(df_1h) >= 20:
                import numpy as _np
                c1h = df_1h["Close"].astype(float)
                # RSI(14) on 1H
                _d  = c1h.diff()
                _ag = _d.clip(lower=0).ewm(com=13, adjust=False).mean()
                _al = (-_d).clip(lower=0).ewm(com=13, adjust=False).mean()
                rsi_1h = float((100 - 100 / (1 + _ag / _al.replace(0, _np.nan))).iloc[-1])
                # MACD on 1H
                _macd_1h = float(
                    (c1h.ewm(span=12, adjust=False).mean()
                     - c1h.ewm(span=26, adjust=False).mean()).iloc[-1])
                # Price vs EMA20 on 1H
                _above_ema_1h = float(c1h.iloc[-1]) > float(
                    c1h.ewm(span=20, adjust=False).mean().iloc[-1])

                h1_bullish = rsi_1h > 55 and _macd_1h > 0 and _above_ema_1h
                h1_bearish = rsi_1h < 45 and _macd_1h < 0 and not _above_ema_1h

                if score > 0 and h1_bullish:
                    score *= 1.08
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Confirms BUY (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bullish: RSI {rsi_1h:.0f}, MACD positive, price above EMA20. "
                                 "All three timeframes (1D, 1W, 1H) align — highest conviction setup."),
                        "sentiment": "pos", "meta": f"1H RSI {rsi_1h:.0f} | MACD {'pos' if _macd_1h > 0 else 'neg'}"})
                elif score > 0 and h1_bearish:
                    score *= 0.82
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Contradicts BUY (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bearish: RSI {rsi_1h:.0f}, MACD negative, price below EMA20. "
                                 "Short-term momentum conflicts with daily BUY — wait for 1H alignment."),
                        "sentiment": "neg", "meta": f"1H RSI {rsi_1h:.0f} | MACD {'pos' if _macd_1h > 0 else 'neg'}"})
                elif score < 0 and h1_bearish:
                    score *= 1.08  # more negative (confirmed bear)
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Confirms SELL (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bearish: RSI {rsi_1h:.0f}, MACD negative, price below EMA20. "
                                 "All three timeframes align bearishly — high-conviction SELL setup."),
                        "sentiment": "neg", "meta": f"1H RSI {rsi_1h:.0f}"})
                elif score < 0 and h1_bullish:
                    score *= 0.82  # less negative (contradicted)
                    sources.add("Technical")
                    rationale.append({"src": "Technical",
                        "head": f"1H Timeframe Contradicts SELL (RSI {rsi_1h:.0f})",
                        "body": (f"1-hour chart is bullish while the daily is bearish. "
                                 "Intraday momentum conflicts with the daily SELL — reduce position or wait."),
                        "sentiment": "pos", "meta": f"1H RSI {rsi_1h:.0f}"})
        except Exception:
            pass  # 1H data unavailable or insufficient — degrade gracefully

        # ── Trend alignment gate (daily 200-DMA) ─────────────────────────────
        # Any BUY signal below the 200-DMA is a counter-trend trade — apply
        # a graded penalty: moderate (-15%) for stocks just under the line,
        # severe (-25%) for stocks deeply below it.
        if sma200:
            below_200_pct = (price / sma200 - 1) * 100
            if score > 0 and price < sma200:
                if below_200_pct < -3:  # deeply below — strong penalty
                    score *= 0.75
                    rationale.append({"src": "Technical", "head": "Counter-Trend BUY Warning",
                        "body": (f"BUY signal in a long-term downtrend. Price (${price:.2f}) is "
                                 f"{abs(below_200_pct):.1f}% below the 200-day MA (${sma200:.2f}). "
                                 "Only the highest-conviction reversals succeed here — reduce size."),
                        "sentiment": "neg", "meta": f"Price vs 200-DMA: {below_200_pct:.1f}%"})
                else:  # within 0–3% below — moderate penalty
                    score *= 0.87
                    rationale.append({"src": "Technical", "head": "200-DMA Trend Gate — Confidence Reduced",
                        "body": (f"BUY signal with price (${price:.2f}) just below the 200-day MA "
                                 f"(${sma200:.2f}). Trend-following BUY signals have lower win rates "
                                 "below this key long-term level. Conviction reduced."),
                        "sentiment": "neg", "meta": f"Price vs 200-DMA: {below_200_pct:.1f}%"})
            elif score < 0 and price > sma200 * 1.05:
                score *= 0.80  # SELL into strong uptrend — harder to play

        # ── Warning Signal De-confliction (Weighted Logic Gate) ─────────────
        # Certain "warning" signals should dynamically reduce position sizing/confidence
        # even if the overall direction is still BUY/SELL. This prevents contradictory
        # signals like "Stochastic Overbought" + "BUY" with high confidence.
        warning_signals = {
            "RSI Overbought", "RSI Elevated", "Stochastic Overbought",
            "Stochastic Bearish Cross (Overbought)", "Williams %R Overbought",
            "CCI Extreme Overbought", "MFI Overbought",
            "Broad Market Complacency", "Extreme Greed",
            "NAAIM: Managers Fully Invested",
        }
        warning_sell_signals = {
            "RSI Oversold", "RSI Weakening", "Stochastic Oversold",
            "Stochastic Bullish Cross (Oversold)", "Williams %R Oversold",
            "CCI Extreme Oversold", "MFI Oversold",
            "Extreme Fear", "Market Breadth Deteriorating",
            "NAAIM: Managers Extremely Defensive",
        }
        
        warning_penalty = 0.0
        warning_rationale = []
        for r in rationale:
            head = r.get("head", "")
            # For BUY signals, penalize overbought warnings
            if score > 0 and head in warning_signals:
                penalty = 0.15  # 15% confidence reduction
                warning_penalty += penalty
                warning_rationale.append({
                    "src": "Risk Gate",
                    "head": f"Warning: {head}",
                    "body": f"This overbought condition reduces conviction in the BUY signal. Consider reducing position size.",
                    "sentiment": "neg",
                    "meta": f"Confidence penalty: -{penalty*100:.0f}%"
                })
            # For SELL signals, penalize oversold warnings
            elif score < 0 and head in warning_sell_signals:
                penalty = 0.15
                warning_penalty += penalty
                warning_rationale.append({
                    "src": "Risk Gate",
                    "head": f"Warning: {head}",
                    "body": f"This oversold condition reduces conviction in the SELL signal. Consider reducing position size.",
                    "sentiment": "neg",
                    "meta": f"Confidence penalty: -{penalty*100:.0f}%"
                })
        
        # Cap warning penalty at 30%; combine with low-volume penalty (cap total at 40%)
        warning_penalty = min(warning_penalty, 0.30)
        rationale.extend(warning_rationale)
        total_confidence_penalty = min(0.40, warning_penalty + vol_confidence_penalty
                                       + rs_confidence_penalty + insider_confidence_penalty)

        # ── Correlation-Based Portfolio Limits ──────────────────────────────
        # Suppress BUY signals when the paper portfolio already has too much
        # exposure in this ticker's sector (default threshold: 30% of portfolio).
        portfolio_ctx = (market_ctx or {}).get("portfolio_ctx", {})
        if portfolio_ctx and score > 0:
            sector_exposure = portfolio_ctx.get("sector_exposure", {})
            ticker_sector   = (sector_rs or {}).get("sector_etf") if sector_rs else None
            if ticker_sector and ticker_sector in sector_exposure:
                exposure_pct = sector_exposure[ticker_sector]
                # Configurable threshold — default 30%; hard suppress above 50%
                SOFT_LIMIT = 30.0
                HARD_LIMIT = 50.0
                if exposure_pct >= HARD_LIMIT:
                    score = 0  # suppress entirely — convert to HOLD
                    sources.add("Risk Gate")
                    rationale.append({
                        "src": "Risk Gate",
                        "head": f"Sector Exposure Limit Hit — {ticker_sector} {exposure_pct:.0f}% of Portfolio",
                        "body": (
                            f"Your paper portfolio already has {exposure_pct:.0f}% of its value in {ticker_sector} "
                            f"sector positions (hard limit: {HARD_LIMIT:.0f}%). "
                            "This BUY signal is suppressed to prevent concentration risk. "
                            "Close an existing position in this sector before adding more."
                        ),
                        "sentiment": "neg",
                        "meta": f"{ticker_sector} exposure: {exposure_pct:.0f}% > {HARD_LIMIT:.0f}% limit",
                    })
                elif exposure_pct >= SOFT_LIMIT:
                    # Soft limit: confidence haircut, not full suppression
                    haircut = min(0.25, (exposure_pct - SOFT_LIMIT) / (HARD_LIMIT - SOFT_LIMIT) * 0.25)
                    total_confidence_penalty = min(0.50, total_confidence_penalty + haircut)
                    sources.add("Risk Gate")
                    rationale.append({
                        "src": "Risk Gate",
                        "head": f"Sector Concentration Warning — {ticker_sector} {exposure_pct:.0f}% of Portfolio",
                        "body": (
                            f"Your paper portfolio has {exposure_pct:.0f}% of its value in {ticker_sector} "
                            f"(soft limit: {SOFT_LIMIT:.0f}%). "
                            "Adding here increases concentration risk. Confidence reduced by "
                            f"{haircut*100:.0f}%. Consider diversifying."
                        ),
                        "sentiment": "neg",
                        "meta": f"{ticker_sector} exposure: {exposure_pct:.0f}% (soft limit {SOFT_LIMIT:.0f}%)",
                    })

        # ── Assemble final signal ───────────────────────────────────────
        agree_sent = "pos" if score > 0 else "neg"
        agreement  = sum(1 for r in rationale if r.get("sentiment") == agree_sent)
        action, confidence = _score_to_action(score, agreement)

        # Apply combined post-processing confidence penalty (warning signals + low volume)
        if total_confidence_penalty > 0 and action in ("BUY", "SELL"):
            confidence = round(max(35.0, confidence * (1 - total_confidence_penalty)), 1)

        # ── Adaptive confidence from historical win rates (VIX-adjusted) ───────
        # In high-volatility regimes, historical win rates are less predictive —
        # patterns break down when VIX is elevated. Dampen the adjustment accordingly.
        adaptive = (market_ctx or {}).get("adaptive_weights", {})
        if adaptive and action in ("BUY", "SELL"):
            wr_key = f"{action}_win_rate"
            win_rate = adaptive.get(wr_key)
            if win_rate is not None:
                # Volatility dampener: reduce the historical-accuracy adjustment under stress
                vix_dampener = 1.0
                if vix is not None:
                    if vix > 30:
                        vix_dampener = 0.40  # panic regimes — history unreliable
                    elif vix > 25:
                        vix_dampener = 0.60
                    elif vix > 20:
                        vix_dampener = 0.80
                wr_delta = round((win_rate - 0.50) * 16 * vix_dampener, 1)
                confidence = round(min(84.0, max(35.0, confidence + wr_delta)), 1)
                if abs(wr_delta) >= 3:
                    sources.add("Backtest")
                    direction_lbl = "boosted" if wr_delta > 0 else "reduced"
                    vix_note = (f" (VIX {vix:.0f} → {vix_dampener:.0%} dampener applied)"
                                if vix is not None and vix_dampener < 1.0 else "")
                    rationale.append({"src": "Backtest",
                        "head": f"Historical {action} Win Rate {win_rate*100:.0f}% — Confidence {direction_lbl}",
                        "body": (f"Past {action} signals have a {win_rate*100:.0f}% win rate. "
                                 f"Confidence adjusted {'+' if wr_delta>0 else ''}{wr_delta:.1f} points.{vix_note}"),
                        "sentiment": "pos" if wr_delta > 0 else "neg",
                        "meta": f"{action} win rate: {win_rate*100:.0f}%"})

        # ── VIX Hard Confidence Floor ────────────────────────────────────────
        # Panic regimes (VIX > 30) mechanically increase realized volatility and
        # the correlation of all risk assets — directional edge deteriorates sharply.
        # Signals below 75% confidence have statistically poor win rates in these
        # conditions: "catching falling knives." Hard-gate to HOLD.
        if vix is not None and vix > 30 and action in ("BUY", "SELL") and confidence < 75:
            action = "HOLD"
            sources.add("Risk Gate")
            rationale.append({
                "src":  "Risk Gate",
                "head": f"VIX Regime Floor — {confidence:.0f}% Below 75% Threshold (VIX {vix:.0f})",
                "body": (
                    f"VIX at {vix:.0f} signals an active panic regime (threshold: 30). "
                    "In elevated-VIX environments, {}-confidence signals have historically poor "
                    "win rates — technical patterns break down as correlations spike and "
                    "liquidity thin outs. Signal gated to HOLD until VIX normalises below 30."
                ).format(f"{confidence:.0f}%"),
                "sentiment": "neg",
                "meta": f"VIX = {vix:.0f} | Min confidence gate: 75% | Actual: {confidence:.0f}%",
            })

        style_map = {"rsi": "intraday", "macd": "swing", "sma": "position"}
        style = style_map.get(dominant, "swing")

        entry, stop, target, rr = _levels(price, atr, action)

        # ── Risk-Free Rate Yield Dampener ────────────────────────────────────
        # Every equity trade competes against the risk-free rate. If the signal's
        # projected return (entry → target) doesn't clear a meaningful risk premium
        # over Treasuries, the trade has negative expected value on a Sharpe basis.
        t10y_rate = ((market_ctx or {}).get("macro") or {}).get("t10y")
        if t10y_rate and t10y_rate > 2.0 and action == "BUY" and entry and target and entry > 0:
            projected_pct = abs(target - entry) / entry * 100
            # Growth / high-beta sectors require a larger premium (investors face more risk)
            sector_etf_key = (sector_rs or {}).get("sector_etf", "")
            high_beta = sector_etf_key in {"XLK", "XLC", "XLY", "XLB"}
            required_premium = 3.5 if high_beta else 2.0   # pp above risk-free
            excess = projected_pct - t10y_rate - required_premium

            if excess < -required_premium:
                # Projected return doesn't even beat the risk-free rate outright
                confidence = round(max(35.0, confidence - 14), 1)
                sources.add("Macro")
                rationale.append({"src": "Macro",
                    "head": f"Risk-Adjusted Return Negative vs Bonds ({projected_pct:.1f}% target vs {t10y_rate:.1f}% risk-free)",
                    "body": (
                        f"Signal target implies a {projected_pct:.1f}% return — below the "
                        f"{t10y_rate:.1f}% 10-Year Treasury yield. Holding risk-free bonds "
                        "dominates this trade on a Sharpe basis. Confidence reduced significantly."
                    ),
                    "sentiment": "neg",
                    "meta": f"Projected {projected_pct:.1f}% | 10Y {t10y_rate:.1f}% | Premium: {excess:.1f}pp"})
            elif excess < 0:
                # Return beats risk-free but misses the required risk premium
                penalty = round(abs(excess) / required_premium * 8, 1)
                confidence = round(max(35.0, confidence - penalty), 1)
                sources.add("Macro")
                rationale.append({"src": "Macro",
                    "head": f"Thin Risk Premium Over Bonds ({projected_pct:.1f}% vs {t10y_rate:.1f}% + {required_premium:.1f}pp premium)",
                    "body": (
                        f"Projected return of {projected_pct:.1f}% only clears the risk-free rate "
                        f"by {projected_pct - t10y_rate:.1f}pp — below the {required_premium:.1f}pp "
                        "risk premium required for this sector's beta. "
                        "The marginal risk-adjusted case is weak."
                    ),
                    "sentiment": "neg",
                    "meta": f"Excess return: {projected_pct - t10y_rate:.1f}pp | Required: {required_premium:.1f}pp"})
            elif excess > required_premium * 2:
                # Generous excess return — genuine edge over risk-free
                boost = min(5.0, excess * 0.3)
                confidence = round(min(84.0, confidence + boost), 1)
                sources.add("Macro")
                rationale.append({"src": "Macro",
                    "head": f"Strong Risk-Adjusted Return ({projected_pct:.1f}% target, {excess:.1f}pp above hurdle)",
                    "body": (
                        f"Signal target of {projected_pct:.1f}% clears the {t10y_rate:.1f}% risk-free rate "
                        f"by {projected_pct - t10y_rate:.1f}pp — {excess:.1f}pp above the "
                        f"{required_premium:.1f}pp required premium. Genuine Sharpe-positive edge."
                    ),
                    "sentiment": "pos",
                    "meta": f"Excess return: {excess:.1f}pp above hurdle | 10Y: {t10y_rate:.1f}%"})
        plain_english = _make_plain_english(action, ticker, style, rationale, confidence, entry, stop, target)

        headline = (
            f"{rationale[0]['head']} · {len(rationale)} signals agree"
            if len(rationale) > 1
            else (rationale[0]["head"] if rationale else f"{action} signal detected")
        )

        # Calibration warning: fires when signal confidence significantly exceeds the
        # historically observed win rate for this action type, or when strong conflicting
        # signals were penalised away but confidence still appears high to the user.
        confidence_warning = False
        if action in ("BUY", "SELL") and confidence >= 75:
            win_rate_hist = (adaptive or {}).get(f"{action}_win_rate")
            if win_rate_hist is not None and confidence - win_rate_hist * 100 > 20:
                confidence_warning = True
            elif total_confidence_penalty >= 0.15:
                confidence_warning = True

        return {
            "ticker":              ticker,
            "company":             info.get("company", ticker),
            "action":              action,
            "confidence":          confidence,
            "confidence_warning":  confidence_warning,
            "price":               price,
            "change":              tech.get("change",     0),
            "changePct":           tech.get("change_pct", 0),
            "entry":               entry,
            "stop":                stop,
            "target":              target,
            "rr":                  rr,
            "headline":            headline,
            "sentiment":           round(avg_sent, 2),
            "style":               style,
            "sources":             sorted(sources),
            "rationale":           rationale,
            "ts":                  datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "session":             _current_session(),
            "daysToEarnings":      days_to_earnings,
            "nextEarningsDate":    earnings_cal.get("next_earnings_date"),
            "sectorEtf":           sector_rs["sector_etf"] if sector_rs else None,
            "rsVsSector":          sector_rs["rs_vs_sector"] if sector_rs else None,
            "plain_english":       plain_english,
        }

    except Exception as e:
        print(f"[signal_engine] {ticker}: {e}")
        return None


async def scan_all(
    tickers: list[str],
    market_ctx: Optional[dict] = None,
    histories: Optional[dict] = None,
    infos: Optional[dict] = None,
) -> list[dict]:
    histories = histories or {}
    infos     = infos     or {}
    results = await asyncio.gather(*[
        generate_signal(
            t,
            market_ctx=market_ctx,
            prefetched_df=histories.get(t),
            prefetched_info=infos.get(t),
        )
        for t in tickers
    ])
    signals = [r for r in results if r is not None]

    # ── Sector Peer Confirmation ─────────────────────────────────────────────
    # Require ≥2 of the tracked peers in the same sector ETF to be BUY before
    # confirming a lone-outlier BUY. Stocks within a sector revert to their mean
    # correlation: a single ticker going up while its sector is flat/down is
    # statistically less reliable than a sector-wide move.
    # Minimum peer count: skip if < 2 sector peers are in the current watchlist.
    sector_map: dict[str, list[dict]] = {}
    for sig in signals:
        etf = sig.get("sectorEtf")
        if etf:
            sector_map.setdefault(etf, []).append(sig)

    for sig in signals:
        if sig.get("action") != "BUY":
            continue
        etf = sig.get("sectorEtf")
        if not etf:
            continue
        peers = [s for s in sector_map.get(etf, []) if s["ticker"] != sig["ticker"]]
        if len(peers) < 2:
            continue  # not enough sector peers in watchlist to form a view

        bullish_peers = [p for p in peers if p.get("action") == "BUY"]
        n_peers       = min(len(peers), 3)   # judge against top-3
        n_bull        = len(bullish_peers)

        if n_bull < 2:
            peer_names = ", ".join(p["ticker"] for p in peers[:3])
            bull_names = ", ".join(p["ticker"] for p in bullish_peers) or "none"
            # Penalty scales with how isolated the signal is
            haircut = 12 if n_bull == 0 else 6
            sig["confidence"] = round(max(35.0, sig["confidence"] - haircut), 1)
            sig["rationale"] = list(sig.get("rationale", [])) + [{
                "src":  "Sector",
                "head": f"Sector Peers Not Confirming BUY — {n_bull}/{n_peers} Bullish ({etf})",
                "body": (
                    f"Of the {len(peers[:3])} {etf}-sector peers on the watchlist "
                    f"({peer_names}), only {n_bull} {'are' if n_bull != 1 else 'is'} bullish "
                    f"({bull_names}). "
                    "Stocks within a sector mean-revert to their cross-sectional correlation: "
                    "a lone-outlier BUY has a materially lower true-positive rate than a "
                    "sector-confirmed move. Confidence reduced."
                ),
                "sentiment": "neg",
                "meta": f"{etf}: {n_bull}/{n_peers} peers bullish | −{haircut}pp confidence",
            }]
            sig["sources"] = sorted(set(sig.get("sources", [])) | {"Sector"})

    return signals
