"""
Scoring helper functions extracted from signal_engine.py.

Each function returns (score_delta, rationale_items, dominant_hint) where:
  score_delta    — float to add to the running score
  rationale_items — list of rationale dicts to extend into the main rationale list
  dominant_hint   — str or None; if set, update `dominant` in the caller

Functions are pure (no side effects, no I/O) and safe to unit-test independently.
"""

from __future__ import annotations

from typing import Optional


def score_oscillators(
    tech: dict,
    rsi: Optional[float],
) -> tuple[float, list[dict], Optional[str]]:
    """Score RSI, Stochastic, Williams %R, and CCI oscillators.

    Returns (osc_delta, rationale_items, dominant_hint).
    Caller adds osc_delta to osc_score and applies the family cap separately.
    """
    osc_delta: float = 0.0
    rationale: list[dict] = []
    dominant_hint: Optional[str] = None

    # ── RSI ──────────────────────────────────────────────────────────────────
    if rsi is not None:
        if rsi < 30:
            osc_delta += 20
            dominant_hint = "rsi"
            rationale.append(
                {
                    "src": "Technical",
                    "head": "RSI Oversold",
                    "body": f"RSI {rsi:.1f} — deeply oversold. Mean-reversion bounce likely.",
                    "sentiment": "pos",
                    "meta": f"RSI(14) = {rsi:.1f}",
                }
            )
        elif rsi < 40:
            osc_delta += 10
            rationale.append(
                {
                    "src": "Technical",
                    "head": "RSI Weakening",
                    "body": f"RSI {rsi:.1f} — approaching oversold territory.",
                    "sentiment": "pos",
                    "meta": f"RSI(14) = {rsi:.1f}",
                }
            )
        elif rsi > 70:
            osc_delta -= 20
            dominant_hint = "rsi"
            rationale.append(
                {
                    "src": "Technical",
                    "head": "RSI Overbought",
                    "body": f"RSI {rsi:.1f} — overbought. Pullback risk elevated.",
                    "sentiment": "neg",
                    "meta": f"RSI(14) = {rsi:.1f}",
                }
            )
        elif rsi > 60:
            osc_delta -= 10
            rationale.append(
                {
                    "src": "Technical",
                    "head": "RSI Elevated",
                    "body": f"RSI {rsi:.1f} — momentum slowing near overbought zone.",
                    "sentiment": "neg",
                    "meta": f"RSI(14) = {rsi:.1f}",
                }
            )

    # ── Stochastic Oscillator %K/%D ───────────────────────────────────────────
    stoch_k = tech.get("stoch_k")
    stoch_d = tech.get("stoch_d")
    stoch_k_prev = tech.get("stoch_k_prev")
    stoch_d_prev = tech.get("stoch_d_prev")
    if stoch_k is not None and stoch_d is not None:
        stoch_cross_up = (
            stoch_k > stoch_d and stoch_k_prev is not None and stoch_d_prev is not None and stoch_k_prev <= stoch_d_prev
        )
        stoch_cross_down = (
            stoch_k < stoch_d and stoch_k_prev is not None and stoch_d_prev is not None and stoch_k_prev >= stoch_d_prev
        )
        if stoch_k < 20 and stoch_cross_up:
            osc_delta += 10
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Stochastic Bullish Cross (Oversold)",
                    "body": "Stochastic %K crossed above %D in oversold zone — high-probability reversal setup.",
                    "sentiment": "pos",
                    "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}",
                }
            )
        elif stoch_k > 80 and stoch_cross_down:
            osc_delta -= 10
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Stochastic Bearish Cross (Overbought)",
                    "body": "Stochastic %K crossed below %D in overbought zone — momentum rolling over.",
                    "sentiment": "neg",
                    "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}",
                }
            )
        elif stoch_k < 25:
            osc_delta += 5
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Stochastic Oversold",
                    "body": f"Stochastic at {stoch_k:.1f} — price is near recent lows. Bounce potential.",
                    "sentiment": "pos",
                    "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}",
                }
            )
        elif stoch_k > 75:
            osc_delta -= 5
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Stochastic Overbought",
                    "body": f"Stochastic at {stoch_k:.1f} — price is near recent highs. Caution.",
                    "sentiment": "neg",
                    "meta": f"K={stoch_k:.1f} D={stoch_d:.1f}",
                }
            )

    # ── Williams %R ───────────────────────────────────────────────────────────
    wr = tech.get("williams_r")
    if wr is not None:
        if wr <= -80:
            osc_delta += 6
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Williams %R Oversold",
                    "body": f"Williams %R at {wr:.1f} — price deeply oversold versus 14-day range.",
                    "sentiment": "pos",
                    "meta": f"W%R = {wr:.1f}",
                }
            )
        elif wr >= -20:
            osc_delta -= 6
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Williams %R Overbought",
                    "body": f"Williams %R at {wr:.1f} — price at top of 14-day range. Resistance likely.",
                    "sentiment": "neg",
                    "meta": f"W%R = {wr:.1f}",
                }
            )

    # ── CCI (Commodity Channel Index) ─────────────────────────────────────────
    cci = tech.get("cci")
    if cci is not None:
        if cci < -150:
            osc_delta += 7
            rationale.append(
                {
                    "src": "Technical",
                    "head": "CCI Extreme Oversold",
                    "body": f"CCI at {cci:.0f} — price far below its statistical average. Reversal watch.",
                    "sentiment": "pos",
                    "meta": f"CCI(20) = {cci:.0f}",
                }
            )
        elif cci < -100:
            osc_delta += 3
        elif cci > 150:
            osc_delta -= 7
            rationale.append(
                {
                    "src": "Technical",
                    "head": "CCI Extreme Overbought",
                    "body": f"CCI at {cci:.0f} — price far above statistical average. Distribution risk.",
                    "sentiment": "neg",
                    "meta": f"CCI(20) = {cci:.0f}",
                }
            )
        elif cci > 100:
            osc_delta -= 3

    return osc_delta, rationale, dominant_hint


def score_macd(
    hist: float,
    hist_p: float,
) -> tuple[float, float, list[dict], Optional[str]]:
    """Score MACD crossover and continuation signals.

    Returns (score_delta, trend_delta, rationale_items, dominant_hint).
    MACD crossovers go directly to score (not the trend family bucket) because
    they are discrete momentum flip events, not continuous trend state.
    """
    score_delta: float = 0.0
    trend_delta: float = 0.0
    rationale: list[dict] = []
    dominant_hint: Optional[str] = None

    cross_up = hist > 0 and hist_p <= 0
    cross_down = hist < 0 and hist_p >= 0

    if cross_up:
        score_delta += 22
        dominant_hint = "macd"
        rationale.append(
            {
                "src": "Technical",
                "head": "MACD Bullish Crossover",
                "body": "MACD crossed above signal line — momentum flipping bullish.",
                "sentiment": "pos",
                "meta": f"Hist {hist:.5f}",
            }
        )
    elif cross_down:
        score_delta -= 22
        dominant_hint = "macd"
        rationale.append(
            {
                "src": "Technical",
                "head": "MACD Bearish Crossover",
                "body": "MACD crossed below signal line — momentum flipping bearish.",
                "sentiment": "neg",
                "meta": f"Hist {hist:.5f}",
            }
        )
    elif hist > 0 and hist > hist_p:
        trend_delta += 10
        rationale.append(
            {
                "src": "Technical",
                "head": "MACD Expanding Bullish",
                "body": "Histogram widening above zero — bullish momentum building.",
                "sentiment": "pos",
                "meta": f"Hist {hist:.5f}",
            }
        )
    elif hist < 0 and hist < hist_p:
        trend_delta -= 10
        rationale.append(
            {
                "src": "Technical",
                "head": "MACD Expanding Bearish",
                "body": "Histogram widening below zero — bearish momentum building.",
                "sentiment": "neg",
                "meta": f"Hist {hist:.5f}",
            }
        )

    return score_delta, trend_delta, rationale, dominant_hint


def score_ema_cross(tech: dict) -> tuple[float, float, list[dict]]:
    """Score EMA 8/21 cross. Returns (score_delta, trend_delta, rationale_items)."""
    score_delta: float = 0.0
    trend_delta: float = 0.0
    rationale: list[dict] = []

    ema8 = tech.get("ema8")
    ema21 = tech.get("ema21")
    ema8_p = tech.get("ema8_prev")
    ema21_p = tech.get("ema21_prev")

    if ema8 and ema21:
        ema_cross_up = ema8 > ema21 and ema8_p is not None and ema21_p is not None and ema8_p <= ema21_p
        ema_cross_down = ema8 < ema21 and ema8_p is not None and ema21_p is not None and ema8_p >= ema21_p
        if ema_cross_up:
            score_delta += 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "EMA 8/21 Bullish Cross",
                    "body": "8-EMA crossed above 21-EMA — short-term momentum turning bullish.",
                    "sentiment": "pos",
                    "meta": f"EMA8 ${ema8:.2f} > EMA21 ${ema21:.2f}",
                }
            )
        elif ema_cross_down:
            score_delta -= 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "EMA 8/21 Bearish Cross",
                    "body": "8-EMA crossed below 21-EMA — short-term momentum turning bearish.",
                    "sentiment": "neg",
                    "meta": f"EMA8 ${ema8:.2f} < EMA21 ${ema21:.2f}",
                }
            )
        elif ema8 > ema21:
            trend_delta += 5
        else:
            trend_delta -= 5

    return score_delta, trend_delta, rationale


def score_obv_adx(
    tech: dict,
    running_score: float,
) -> tuple[float, float, list[dict]]:
    """Score OBV and ADX. Returns (volume_delta, trend_delta, rationale_items).

    running_score is the current accumulated score — OBV uses it to decide
    whether the confirmation bonus is 10 (aligns with trend) or 4 (weak alignment).
    """
    volume_delta: float = 0.0
    trend_delta: float = 0.0
    rationale: list[dict] = []

    # ── OBV ──────────────────────────────────────────────────────────────────
    obv_above = tech.get("obv_above")
    obv_slope = tech.get("obv_slope", 0) or 0
    if obv_above is not None:
        if obv_above and obv_slope > 0:
            bonus = 10 if running_score > 0 else 4
            volume_delta += bonus
            rationale.append(
                {
                    "src": "Technical",
                    "head": "OBV Bullish — Volume Accumulation",
                    "body": "On-Balance Volume trending up and above its 20-day MA. Smart money accumulating.",
                    "sentiment": "pos",
                    "meta": f"OBV slope: +{obv_slope:,.0f} shares",
                }
            )
        elif not obv_above and obv_slope < 0:
            bonus = -10 if running_score < 0 else -4
            volume_delta += bonus
            rationale.append(
                {
                    "src": "Technical",
                    "head": "OBV Bearish — Volume Distribution",
                    "body": "On-Balance Volume trending down and below its 20-day MA. Distribution pressure.",
                    "sentiment": "neg",
                    "meta": f"OBV slope: {obv_slope:,.0f} shares",
                }
            )

    # ── ADX ──────────────────────────────────────────────────────────────────
    adx = tech.get("adx")
    plus_di = tech.get("adx_plus_di")
    minus_di = tech.get("adx_minus_di")
    if adx is not None and plus_di is not None and minus_di is not None:
        if adx > 25:
            if plus_di > minus_di:
                trend_delta += 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"ADX Strong Uptrend (ADX {adx:.0f})",
                        "body": f"ADX at {adx:.0f} confirms a strong directional uptrend. +DI ({plus_di:.0f}) dominates -DI ({minus_di:.0f}).",
                        "sentiment": "pos",
                        "meta": f"ADX={adx:.0f} +DI={plus_di:.0f} -DI={minus_di:.0f}",
                    }
                )
            else:
                trend_delta -= 8
                rationale.append(
                    {
                        "src": "Technical",
                        "head": f"ADX Strong Downtrend (ADX {adx:.0f})",
                        "body": f"ADX at {adx:.0f} confirms a strong directional downtrend. -DI ({minus_di:.0f}) dominates +DI ({plus_di:.0f}).",
                        "sentiment": "neg",
                        "meta": f"ADX={adx:.0f} +DI={plus_di:.0f} -DI={minus_di:.0f}",
                    }
                )

    return volume_delta, trend_delta, rationale


def score_moving_averages(
    price: float,
    sma50: Optional[float],
    sma200: Optional[float],
    poly_ind: dict,
) -> tuple[float, list[dict]]:
    """Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.

    Returns (ma_delta, rationale_items). Caller applies the ±22 family cap.
    """
    ma_delta: float = 0.0
    rationale: list[dict] = []

    if sma200:
        if price > sma200 * 1.01:
            ma_delta += 15
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Above 200-DMA",
                    "body": f"Price ${price:.2f} is {(price / sma200 - 1) * 100:.1f}% above 200-day MA. Long-term uptrend.",
                    "sentiment": "pos",
                    "meta": f"200-DMA ${sma200:.2f}",
                }
            )
        elif price < sma200 * 0.99:
            ma_delta -= 15
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Below 200-DMA",
                    "body": f"Price ${price:.2f} is below the 200-day MA — long-term downtrend.",
                    "sentiment": "neg",
                    "meta": f"200-DMA ${sma200:.2f}",
                }
            )

    if sma50:
        ma_delta += 8 if price > sma50 else -8

    if sma50 and sma200:
        if sma50 > sma200 * 1.005:
            ma_delta += 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Golden Cross Active",
                    "body": f"50-DMA (${sma50:.0f}) above 200-DMA (${sma200:.0f}). Strong long-term bullish structure.",
                    "sentiment": "pos",
                    "meta": "50-DMA > 200-DMA",
                }
            )
        elif sma50 < sma200 * 0.995:
            ma_delta -= 12
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Death Cross Active",
                    "body": f"50-DMA (${sma50:.0f}) below 200-DMA (${sma200:.0f}). Long-term bearish structure.",
                    "sentiment": "neg",
                    "meta": "50-DMA < 200-DMA",
                }
            )

    # EMA(200) double-confirmation
    ema200 = poly_ind.get("ema200") if poly_ind else None
    if ema200 and sma200:
        above_ema200 = price > ema200
        above_sma200 = price > sma200
        if above_ema200 and above_sma200:
            ma_delta += 3
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Double Bullish: Above EMA200 & SMA200",
                    "body": (
                        f"Price ${price:.2f} is above both EMA(200) (${ema200:.2f}) and SMA(200) (${sma200:.2f}). "
                        "Institutional algorithms use EMA(200) as a trend filter — double confirmation reduces false signals."
                    ),
                    "sentiment": "pos",
                    "meta": f"EMA200=${ema200:.2f} SMA200=${sma200:.2f}",
                }
            )
        elif not above_ema200 and not above_sma200:
            ma_delta -= 3
            rationale.append(
                {
                    "src": "Technical",
                    "head": "Double Bearish: Below EMA200 & SMA200",
                    "body": (
                        f"Price ${price:.2f} is below both EMA(200) (${ema200:.2f}) and SMA(200) (${sma200:.2f}). "
                        "Confirmed long-term downtrend by both smoothing methods."
                    ),
                    "sentiment": "neg",
                    "meta": f"EMA200=${ema200:.2f} SMA200=${sma200:.2f}",
                }
            )

    return ma_delta, rationale
