"""
§64 yield curve, §65 TRIN, §66 AD breadth, §68 T10Y rate-of-change gates.

All four gates read only from the `macro` context dict and the current sector.
None of them can flip action to HOLD — they only adjust confidence up/down and
add rationale cards. This makes them safe to apply in any order after the main
scoring step.

Public API:
    score_macro_extensions(action, confidence, macro, sector_etf)
        -> (new_confidence, cards, new_sources)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SignalContext


def score_macro_extensions(
    action: str,
    confidence: float,
    macro: dict,
    sector_etf: str | None,
) -> tuple[float, list[dict], set[str]]:
    """
    Apply §64/§65/§66/§68 macro extension gates and return updated confidence.

    Args:
        action:     current signal action ("BUY" / "SELL" / "HOLD")
        confidence: current confidence value (0–100)
        macro:      macro context dict from macro.py
        sector_etf: sector ETF ticker (e.g. "XLF", "XLK") or None

    Returns:
        (new_confidence, cards, new_sources)
        cards is a list of rationale dicts to extend the main rationale list.
        new_sources is a set of source strings to add to the main sources set.
    """
    cards: list[dict] = []
    new_sources: set[str] = set()
    etf = (sector_etf or "").upper()

    # ── §65 TRIN/Arms Index — Market-Wide Capitulation ────────────────────
    _trin = macro.get("trin")
    if action == "BUY" and _trin is not None and _trin > 2.0:
        confidence = round(min(72.0, confidence + 4), 1)
        new_sources.add("Macro")
        cards.append(
            {
                "src": "Macro",
                "head": f"TRIN {_trin:.2f} — Market-Wide Capitulation",
                "body": (
                    f"TRIN (Arms Index) of {_trin:.2f} > 2.0 signals extreme market-wide "
                    "selling pressure. Historically, TRIN spikes above 2 accompany "
                    "short-term capitulation lows — mean-reversion setups entered here "
                    "have significantly above-average win rates."
                ),
                "sentiment": "pos",
                "meta": f"TRIN={_trin:.2f} (>2.0 = capitulation; §65)",
            }
        )

    # ── §66 Zweig Breadth Thrust / AD Breadth ─────────────────────────────
    _zweig = macro.get("zweig_thrust")
    _ad_chg = macro.get("ad_ema10_chg")
    if action == "BUY" and _zweig:
        confidence = round(min(72.0, confidence + 5), 1)
        new_sources.add("Macro")
        cards.append(
            {
                "src": "Macro",
                "head": "Zweig Breadth Thrust — Broad Market Recovery Confirmed",
                "body": (
                    "A Zweig Breadth Thrust has fired: the 10-day EMA of advancing issues "
                    "crossed from negative to above +50. Historically (91% WR since 1950) "
                    "this signals the start of a sustained broad-market advance — mean-reversion "
                    "entries here benefit from a rising tide."
                ),
                "sentiment": "pos",
                "meta": "zweig_thrust=True (§66)",
            }
        )
    elif _ad_chg is not None and _ad_chg < -200 and action == "BUY":
        confidence = round(max(35.0, confidence - 3), 1)
        new_sources.add("Macro")
        cards.append(
            {
                "src": "Macro",
                "head": f"Breadth Deteriorating (AD 10d EMA Chg {_ad_chg:+.0f}) — −3pp",
                "body": (
                    f"10-day EMA of daily advance/decline change is {_ad_chg:+.0f}, "
                    "indicating broad-market breadth deterioration. Individual stock "
                    "MR entries in a weakening-breadth environment have lower follow-through."
                ),
                "sentiment": "neg",
                "meta": f"ad_ema10_chg={_ad_chg:.0f} (<-200 = breadth deteriorating; §66)",
            }
        )

    # ── §64 Yield Curve — XLF Sector Penalty ──────────────────────────────
    _t10y2y = macro.get("t10y2y_spread")
    if _t10y2y is not None and _t10y2y < -0.5 and etf == "XLF" and action == "BUY":
        confidence = round(max(35.0, confidence - 5), 1)
        new_sources.add("Macro")
        cards.append(
            {
                "src": "Macro",
                "head": f"Inverted Yield Curve (T10Y2Y {_t10y2y:+.2f}%) — XLF Penalty",
                "body": (
                    f"10Y–2Y Treasury spread of {_t10y2y:+.2f}% is deeply inverted. "
                    "Inverted curves compress bank net-interest margins — financial sector "
                    "MR entries in this regime have materially lower win rates. −5pp penalty."
                ),
                "sentiment": "neg",
                "meta": f"t10y2y_spread={_t10y2y:.2f}% (<-0.5 + XLF; §64)",
            }
        )

    # ── §68 T10Y Rate of Change — XLK Penalty / Equity Tailwind ──────────
    _t10y_chg = macro.get("t10y_30d_chg")
    if _t10y_chg is not None and action == "BUY":
        if _t10y_chg > 0.5 and etf == "XLK":
            confidence = round(max(35.0, confidence - 6), 1)
            new_sources.add("Macro")
            cards.append(
                {
                    "src": "Macro",
                    "head": f"Rising Rates ({_t10y_chg:+.2f}pp in 30d) — XLK Headwind",
                    "body": (
                        f"10Y Treasury yield rose {_t10y_chg:+.2f}pp over the past 30 days. "
                        "Rising long-end rates compress tech/growth valuations via discount "
                        "rate expansion — XLK MR entries in a rising-rate regime fail more often."
                    ),
                    "sentiment": "neg",
                    "meta": f"t10y_30d_chg={_t10y_chg:+.2f}pp (>0.5 + XLK; §68)",
                }
            )
        elif _t10y_chg < -0.3:
            confidence = round(min(72.0, confidence + 3), 1)
            new_sources.add("Macro")
            cards.append(
                {
                    "src": "Macro",
                    "head": f"Falling Rates ({_t10y_chg:+.2f}pp in 30d) — Equity Tailwind",
                    "body": (
                        f"10Y Treasury yield fell {abs(_t10y_chg):.2f}pp over the past 30 days. "
                        "Declining long-end rates lower the equity discount rate — positive "
                        "for duration-sensitive growth stocks and supportive of MR bounces."
                    ),
                    "sentiment": "pos",
                    "meta": f"t10y_30d_chg={_t10y_chg:+.2f}pp (<-0.3 = rate tailwind; §68)",
                }
            )

    return confidence, cards, new_sources


# ── GateBase class (Strategy Pattern API) ─────────────────────────────────────


class MacroExtensionsGate:
    """
    GateBase wrapper around score_macro_extensions().
    Use in a GatePipeline; the functional API above is kept for direct calls.
    """

    # Avoid importing GateBase at module level to prevent circular imports;
    # the duck-typing interface (apply method) satisfies GatePipeline.run().
    def apply(self, ctx: SignalContext) -> None:

        ctx.confidence, _cards, _srcs = score_macro_extensions(
            action=ctx.action,
            confidence=ctx.confidence,
            macro=ctx.macro,
            sector_etf=ctx.sector_etf,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def __repr__(self) -> str:
        return "MacroExtensionsGate"
