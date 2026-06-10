"""
services/engines/scorers.py

Decomposed scoring blocks utilizing the ScoringContext object.
"""

import logging
from services.engines.context import ScoringContext

log = logging.getLogger("signal.trade.scorers")


def score_moving_averages_block(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages

    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}

    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)

    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))


def score_bollinger_bands_block(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price

    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = (
                    f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
                )
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append(
                {
                    "src": "Technical",
                    "head": "BB Extreme Oversold",
                    "body": bb_body,
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
                }
            )
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append(
                    {
                        "src": "Technical",
                        "head": "BB Oversold + RSI Confirmed",
                        "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                        "sentiment": "pos",
                        "meta": f"BB%B={bb_pct_b:.2f}",
                    }
                )
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append(
                    {
                        "src": "Technical",
                        "head": "BB Near Lower Band",
                        "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                        "sentiment": "pos",
                        "meta": f"BB%B={bb_pct_b:.2f}",
                    }
                )
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append(
                    {
                        "src": "Technical",
                        "head": "BB Extreme Overbought",
                        "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                        "sentiment": "neg",
                        "meta": f"BB%B={bb_pct_b:.2f}",
                    }
                )
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append(
                {
                    "src": "Technical",
                    "head": "Lower Bollinger Band Touch",
                    "body": "Price at lower BB — potential mean-reversion bounce.",
                    "sentiment": "pos",
                    "meta": f"BB Lower ${bb_lower:.2f}",
                }
            )
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append(
                {
                    "src": "Technical",
                    "head": "Upper Bollinger Band Touch",
                    "body": "Price at upper BB — potential overextension.",
                    "sentiment": "neg",
                    "meta": f"BB Upper ${bb_upper:.2f}",
                }
            )
