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

    # ── §77 52-Week-Low Structural Decline — HARD BLOCK (strengthened 2026-07-14) ──
    # History of this gate: +4pp tax-loss boost (theory) → INVERTED to −4pp
    # penalty 2026-05-31 (live: WR 31.0% near 52-wk low, −11.5pp vs baseline)
    # → HARD BLOCK 2026-07-14. Gate audit on the exit-chronology-corrected
    # book: the −4pp cohort STILL resolved at ΔWR −16.4pp / avg net −0.46%
    # per trade (N=21 delivered) — the penalty was far too weak to gate a
    # cohort this bad. Near-annual-low = structural decline, not recoverable
    # oversold; these BUYs are now converted to HOLD.
    _wk52l = info.get("week_52_low")
    if action == "BUY" and _wk52l and price and price > 0:
        _near_low = (_wk52l > 0) and (price <= _wk52l * 1.08)
        if _near_low:
            action = "HOLD"
            new_sources.add("Risk Gate")
            cards.append(
                {
                    "src": "Risk Gate",
                    "head": "Near 52-Week Low — Structural Decline, BUY Blocked (§77)",
                    "body": (
                        f"Price is within 8% of the 52-week low ({_wk52l:.2f}). "
                        "Live-data audits (546 trades 2026-05: WR 31%; corrected book "
                        "2026-07: ΔWR −16.4pp, negative net EV) show these stocks are in "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. The earlier −4pp penalty was too weak; BUY is blocked."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True hard_block §77 (penalty→block 2026-07-14)",
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
