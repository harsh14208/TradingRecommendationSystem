"""Warning de-confliction helpers for overbought/oversold technical heads.

These are probability adjustments driven by conflicting evidence in the
rationale (e.g., a BUY signal that also contains an overbought reading).
They mutate the *raw* confidence estimate and feed into calibration; they do
not mutate calibrated probability directly.
"""

from __future__ import annotations

# Heads that conflict with a BUY signal: the setup claims the stock is
# overbought while simultaneously recommending to buy. Trim conviction.
_BUY_OVERBOUGHT_HEADS = frozenset(
    {
        "RSI Overbought",
        "RSI Elevated",
        "Stochastic Overbought",
        "Stochastic Bearish Cross (Overbought)",
        "Williams %R Overbought",
        "CCI Extreme Overbought",
        "MFI Overbought",
        "Broad Market Complacency",
        "Extreme Greed",
        "NAAIM: Managers Fully Invested",
    }
)

# Heads that conflict with a SELL signal: the setup claims the stock is
# oversold while recommending to sell. Trim conviction.
_SELL_OVERSOLD_HEADS = frozenset(
    {
        "RSI Oversold",
        "RSI Weakening",
        "Stochastic Oversold",
        "Stochastic Bullish Cross (Oversold)",
        "Williams %R Oversold",
        "CCI Extreme Oversold",
        "MFI Oversold",
        "Extreme Fear",
        "Market Breadth Deteriorating",
        "NAAIM: Managers Extremely Defensive",
    }
)

# Small confidence haircut applied when conflicting warning heads are present.
# Chosen so that a 72% confidence becomes 66.2% (still above most sizing tiers)
# and a 40% confidence becomes 36.8% (above the 35% floor).
_WARNING_HAIRCUT = 0.92
_CONFIDENCE_FLOOR = 35.0


def _has_conflicting_head(action: str, rationale: list[dict]) -> bool:
    """Return True if rationale contains a head that conflicts with action."""
    if action == "BUY":
        target_heads = _BUY_OVERBOUGHT_HEADS
    elif action == "SELL":
        target_heads = _SELL_OVERSOLD_HEADS
    else:
        return False
    return any(r.get("head") in target_heads for r in rationale)


def apply_warning_deconfliction(action: str, raw_confidence: float, rationale: list[dict]) -> float:
    """Apply a small confidence haircut when conflicting warning heads exist.

    Parameters
    ----------
    action:
        Signal action ("BUY", "SELL", or "HOLD").
    raw_confidence:
        Pre-calibration confidence estimate.
    rationale:
        List of rationale card dicts; each should contain a "head" key.

    Returns
    -------
    Adjusted raw confidence, floored at ``_CONFIDENCE_FLOOR``.  For ``HOLD``
    actions the confidence is returned unchanged.
    """
    if action not in ("BUY", "SELL"):
        return raw_confidence
    if not _has_conflicting_head(action, rationale):
        return raw_confidence
    return round(max(_CONFIDENCE_FLOOR, raw_confidence * _WARNING_HAIRCUT), 1)
