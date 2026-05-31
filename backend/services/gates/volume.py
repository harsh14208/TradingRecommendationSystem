"""
Volume, momentum-quality, and liquidity gates extracted from _assemble_signal().

Gates (applied in pipeline order):
  RvolGate             — RVOL BUY prerequisite (regime-adaptive threshold)
  AdxGate              — ADX minimum (no entries in directionless markets)
  OverboughtWeakTrendGate — RSI overbought + fading ADX topping filter
  DollarVolumeGate     — thin liquidity confidence haircut + low-ATR disclosure

Each gate is independently unit-testable:
    ctx = SignalContext(action="BUY", confidence=65.0, score=52.0,
                        rationale=[], sources=set(), ...)
    RvolGate().apply(ctx)
    assert ctx.action == "HOLD"
"""

from __future__ import annotations

from .base import GateBase, SignalContext


class RvolGate(GateBase):
    """
    RVOL BUY prerequisite (regime-adaptive threshold).

    Normal regime  (ADR compressed): requires RVOL ≥ 1.2×.
    Expanded regime (ADR elevated) : requires RVOL ≥ 1.0×.
    Waiver: RSI < 30 (pure oversold bounce — no volume confirmation needed).
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        volume = ctx.tech.get("volume") or 0
        avg_vol = ctx.tech.get("avg_volume") or 0
        if avg_vol <= 0:
            return  # no volume data — skip gate
        vol_ratio = volume / avg_vol
        is_oversold = ctx.tech.get("rsi") is not None and ctx.tech.get("rsi") < 30
        if is_oversold:
            return
        adr_compressed = ctx.tech.get("adr_compression", True)
        threshold = 1.2 if adr_compressed else 1.0
        if vol_ratio < threshold:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"RVOL Gate — Insufficient Volume ({vol_ratio:.1f}× < {threshold:.1f}×)",
                    "body": (
                        f"BUY signals require Relative Volume (RVOL) ≥ {threshold:.1f}× to confirm "
                        "institutional participation. Low-volume breakouts fail at high rates "
                        "regardless of score. Oversold bounce (RSI < 30) is the only waiver. "
                        + (
                            "Vol regime: expanded (ADR not compressed) — threshold relaxed to 1.0×."
                            if not adr_compressed
                            else "Vol regime: normal — standard 1.2× threshold applied."
                        )
                    ),
                    "sentiment": "neg",
                    "meta": f"RVOL {vol_ratio:.1f}× < {threshold:.1f}× | adr_compressed={adr_compressed}",
                }
            )


class AdxGate(GateBase):
    """
    ADX minimum gate — no entries in completely directionless markets.

    Fires when ADX < 18 and RSI ≥ 30 and score < 45.
    Waived for deep-oversold bounces (RSI < 30) where MR works even flat.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        adx = ctx.tech.get("adx")
        rsi = float(ctx.tech.get("rsi") or 50)
        if adx is None:
            return
        if float(adx) < 18 and rsi >= 30 and ctx.score < 45:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"ADX Minimum Gate — ADX {float(adx):.0f} < 18 (No Trend)",
                    "body": (
                        f"ADX at {float(adx):.0f} — market is directionless. Momentum crossovers "
                        "and breakout signals whipsaw in choppy flat markets. Requiring ADX ≥ 18 "
                        "to confirm a minimum directional trend before issuing BUY."
                    ),
                    "sentiment": "neg",
                    "meta": f"ADX={float(adx):.1f} < 18 | Score={ctx.score:.1f}",
                }
            )


class OverboughtWeakTrendGate(GateBase):
    """
    RSI overbought + weak trend gate (topping market filter).

    Fires when RSI > 70 AND ADX < 28 AND sp500_trend == "up" AND score < 40.
    When ADX ≥ 28, RSI > 70 is a valid momentum continuation — not fired.
    """

    def apply(self, ctx: SignalContext) -> None:
        if ctx.action != "BUY":
            return
        rsi = float(ctx.tech.get("rsi") or 50)
        adx = ctx.tech.get("adx")
        adx_val = float(adx) if adx is not None else 25.0
        if ctx.sp500_trend == "up" and rsi > 70 and adx_val < 28 and ctx.score < 40:
            ctx.action = "HOLD"
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Overbought + Weak Trend Gate — RSI {rsi:.0f}, ADX {adx_val:.0f}",
                    "body": (
                        f"RSI at {rsi:.0f} (overbought) while ADX at {adx_val:.0f} (weak trend). "
                        "This pattern — extended price + fading momentum — precedes reversals in bull "
                        "markets. When ADX ≥ 28 (strong trend), RSI > 70 is a valid continuation; "
                        "below 28 it is a topping signal. Marginal score blocked."
                    ),
                    "sentiment": "neg",
                    "meta": f"RSI={rsi:.1f} | ADX={adx_val:.1f} < 28 | Score={ctx.score:.1f}",
                }
            )


class DollarVolumeGate(GateBase):
    """
    Thin dollar-volume confidence haircut + low-ATR regime disclosure.

    Dollar volume < $5M/day → −4pp or −8pp confidence haircut (soft gate,
    not HOLD).  Low-ATR regime annotation fires regardless of action.
    """

    def apply(self, ctx: SignalContext) -> None:
        # Dollar-volume haircut
        dollar_vol = ctx.price * (ctx.tech.get("volume") or 0) if ctx.price else 0
        if ctx.action in ("BUY", "SELL") and 0 < dollar_vol < 5_000_000:
            pen = 8 if dollar_vol < 1_000_000 else 4
            ctx.confidence = round(max(35.0, ctx.confidence - pen), 1)
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Thin Dollar Volume — ${dollar_vol / 1e6:.1f}M/day ({pen}pp confidence haircut)",
                    "body": (
                        f"Daily dollar volume of ${dollar_vol / 1e6:.1f}M is below the $5M threshold. "
                        "Thin liquidity means bid-ask spread costs erode signal edge, and large orders "
                        "move price against the position. Use a smaller position size."
                    ),
                    "sentiment": "neg",
                    "meta": f"dollar_vol=${dollar_vol / 1e6:.1f}M | penalty={pen}pp",
                }
            )

        # Low-ATR regime disclosure (informational — fires regardless of action)
        if ctx.is_low_atr:
            ctx.sources.add("Risk Gate")
            ctx.rationale.append(
                {
                    "src": "Risk Gate",
                    "head": "Low-ATR Regime Switch Active — Momentum Bypassed",
                    "body": (
                        f"ATR is only {ctx.atr_pct_pre * 100:.2f}% of price — structurally range-bound stock. "
                        "Trend and momentum scoring families (MACD state, MA cross, ADX, ROC, Donchian) "
                        "have been bypassed. Only mean-reversion signals (Bollinger, Z-score, RSI oversold, "
                        "pivot support) are scored. This reduces false BUY signals on KO/PEP/T-style tickers."
                    ),
                    "sentiment": "neg" if ctx.action == "HOLD" else "pos",
                    "meta": f"low_atr_regime=True atr_pct={ctx.atr_pct_pre * 100:.2f}%",
                }
            )
