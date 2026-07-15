"""
Calendar and seasonal gates: §77 tax-loss harvesting window.

Time-based adjustment with no dependency on live market data beyond the
signal's own price and basic fundamentals. §77 only adjusts confidence.
(§57 Friday HOLD-flip removed 2026-07-14 — unvalidated; the validated §57
Thursday threshold lives in delivery_gates.py.)

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
    Apply the §77 tax-loss seasonal gate.

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

    # §57 Friday HOLD-flip — REMOVED 2026-07-14 (gate audit)
    # This silent BUY→HOLD conversion claimed "20yr backtest ~0.40%" but has
    # NO entry in the validation ledger — the only §57 component that was
    # actually ablated is the *Thursday* strict threshold in delivery_gates
    # (ΔSharpe −0.10 on removal, the largest validated gate — kept). An
    # unaudited action-flip is the most dangerous gate shape; if a Friday
    # effect is real it must earn a ledger entry via --validate-live-gates
    # before coming back.

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
