"""
Calendar and seasonal gates: §57 DOW gate and §77 tax-loss harvesting window.

Both gates are time-based adjustments with no dependency on live market data
beyond the signal's own price and basic fundamentals.

§57 DOW gate can flip action to HOLD (Friday entries with score<65).
§77 tax-loss window only adjusts confidence.

Public API:
    apply_calendar_gates(action, confidence, score, today_dow, month, price, info)
        -> (new_action, new_confidence, cards, new_sources)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SignalContext


def apply_calendar_gates(
    action: str,
    confidence: float,
    score: float,
    today_dow: int,
    month: int,
    price: float | None,
    info: dict,
) -> tuple[str, float, list[dict], set[str]]:
    """
    Apply §57 DOW gate and §77 tax-loss seasonal gate.

    Args:
        action:    current signal action
        confidence: current confidence value (0–100)
        score:     raw alpha score (used by DOW gate exemption threshold)
        today_dow: weekday integer, 0=Monday … 4=Friday
        month:     calendar month (1–12)
        price:     current price (may be None)
        info:      ticker info dict (must contain "week_52_low" for §77)

    Returns:
        (new_action, new_confidence, cards, new_sources)
    """
    cards: list[dict] = []
    new_sources: set[str] = set()

    # ── §57 Day-of-Week Gate — No Friday BUY Entries ──────────────────────
    # Friday entries carry 2-day weekend gap risk with no intraday management.
    # 20yr backtest: Friday entries underperform Mon-Thu by ~0.40% avg return.
    # High-conviction signals (score≥65) are exempt — the edge is strong enough
    # to overcome the weekend-gap risk.
    if action == "BUY" and today_dow == 4 and score < 65:
        action = "HOLD"
        new_sources.add("Risk Gate")
        cards.append(
            {
                "src": "Risk Gate",
                "head": "Day-of-Week Gate — No Friday Entries (Weekend Gap Risk)",
                "body": (
                    "Friday BUY entries face a mandatory 2-day hold through the weekend with no "
                    "intraday management capability. 20yr backtest: Friday entries underperform "
                    "Mon–Thu by ~0.40% avg return due to gap-open risk. "
                    "Signals with score≥65 (strong alt-data confirmation) are exempt."
                ),
                "sentiment": "neg",
                "meta": f"weekday=Friday(4) score={score:.1f}<65 | dow_gate=True",
            }
        )
        return action, confidence, cards, new_sources  # terminal: DOW gate fires

    # ── §77 Tax-Loss Harvesting Window — INVERTED 2026-05-31 ─────────────────
    # Live-data audit (Inv 3, 546 resolved signals): signals near 52-week low
    # have WR=31.0% (−11.5pp vs baseline 42.5%). The academic tax-loss recovery
    # hypothesis does not hold in our 10-day MR system — stocks near 52-week lows
    # are in structural decline, not recoverable oversold. The prior +4pp boost was
    # actively harmful. Replaced with a −4pp penalty: near-annual-low = structural
    # seller pressure, not a temporary dislocation.
    _wk52l = info.get("week_52_low")
    if action == "BUY" and _wk52l and price and price > 0:
        _near_low = (_wk52l > 0) and (price <= _wk52l * 1.08)
        if _near_low:
            confidence = round(max(35.0, confidence - 4), 1)
            new_sources.add("Risk Gate")
            cards.append(
                {
                    "src": "Risk Gate",
                    "head": "Near 52-Week Low — Structural Decline Risk −4pp (§77)",
                    "body": (
                        f"Price is within 8% of the 52-week low ({_wk52l:.2f}). "
                        "Live-data audit (546 trades): signals near 52-week lows win only "
                        "31% of the time (−11.5pp vs baseline). These stocks are in "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


# ── GateBase class (Strategy Pattern API) ─────────────────────────────────────


class CalendarGate:
    """
    GateBase wrapper around apply_calendar_gates().
    Use in a GatePipeline; the functional API above is kept for direct calls.
    """

    def apply(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def __repr__(self) -> str:
        return "CalendarGate"
