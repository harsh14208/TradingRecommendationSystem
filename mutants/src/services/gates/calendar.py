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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_apply_calendar_gates__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_apply_calendar_gates__mutmut)
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


def x_apply_calendar_gates__mutmut_orig(
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


def x_apply_calendar_gates__mutmut_1(
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
    cards: list[dict] = None
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


def x_apply_calendar_gates__mutmut_2(
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
    new_sources: set[str] = None

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


def x_apply_calendar_gates__mutmut_3(
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
    if action == "BUY" and today_dow == 4 or score < 65:
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


def x_apply_calendar_gates__mutmut_4(
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
    if action == "BUY" or today_dow == 4 and score < 65:
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


def x_apply_calendar_gates__mutmut_5(
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
    if action != "BUY" and today_dow == 4 and score < 65:
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


def x_apply_calendar_gates__mutmut_6(
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
    if action == "XXBUYXX" and today_dow == 4 and score < 65:
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


def x_apply_calendar_gates__mutmut_7(
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
    if action == "buy" and today_dow == 4 and score < 65:
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


def x_apply_calendar_gates__mutmut_8(
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
    if action == "BUY" and today_dow != 4 and score < 65:
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


def x_apply_calendar_gates__mutmut_9(
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
    if action == "BUY" and today_dow == 5 and score < 65:
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


def x_apply_calendar_gates__mutmut_10(
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
    if action == "BUY" and today_dow == 4 and score <= 65:
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


def x_apply_calendar_gates__mutmut_11(
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
    if action == "BUY" and today_dow == 4 and score < 66:
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


def x_apply_calendar_gates__mutmut_12(
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
        action = None
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


def x_apply_calendar_gates__mutmut_13(
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
        action = "XXHOLDXX"
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


def x_apply_calendar_gates__mutmut_14(
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
        action = "hold"
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


def x_apply_calendar_gates__mutmut_15(
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
        new_sources.add(None)
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


def x_apply_calendar_gates__mutmut_16(
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
        new_sources.add("XXRisk GateXX")
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


def x_apply_calendar_gates__mutmut_17(
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
        new_sources.add("risk gate")
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


def x_apply_calendar_gates__mutmut_18(
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
        new_sources.add("RISK GATE")
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


def x_apply_calendar_gates__mutmut_19(
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
            None
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


def x_apply_calendar_gates__mutmut_20(
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
                "XXsrcXX": "Risk Gate",
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


def x_apply_calendar_gates__mutmut_21(
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
                "SRC": "Risk Gate",
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


def x_apply_calendar_gates__mutmut_22(
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
                "src": "XXRisk GateXX",
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


def x_apply_calendar_gates__mutmut_23(
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
                "src": "risk gate",
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


def x_apply_calendar_gates__mutmut_24(
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
                "src": "RISK GATE",
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


def x_apply_calendar_gates__mutmut_25(
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
                "XXheadXX": "Day-of-Week Gate — No Friday Entries (Weekend Gap Risk)",
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


def x_apply_calendar_gates__mutmut_26(
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
                "HEAD": "Day-of-Week Gate — No Friday Entries (Weekend Gap Risk)",
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


def x_apply_calendar_gates__mutmut_27(
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
                "head": "XXDay-of-Week Gate — No Friday Entries (Weekend Gap Risk)XX",
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


def x_apply_calendar_gates__mutmut_28(
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
                "head": "day-of-week gate — no friday entries (weekend gap risk)",
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


def x_apply_calendar_gates__mutmut_29(
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
                "head": "DAY-OF-WEEK GATE — NO FRIDAY ENTRIES (WEEKEND GAP RISK)",
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


def x_apply_calendar_gates__mutmut_30(
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
                "XXbodyXX": (
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


def x_apply_calendar_gates__mutmut_31(
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
                "BODY": (
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


def x_apply_calendar_gates__mutmut_32(
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
                    "XXFriday BUY entries face a mandatory 2-day hold through the weekend with no XX"
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


def x_apply_calendar_gates__mutmut_33(
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
                    "friday buy entries face a mandatory 2-day hold through the weekend with no "
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


def x_apply_calendar_gates__mutmut_34(
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
                    "FRIDAY BUY ENTRIES FACE A MANDATORY 2-DAY HOLD THROUGH THE WEEKEND WITH NO "
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


def x_apply_calendar_gates__mutmut_35(
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
                    "XXintraday management capability. 20yr backtest: Friday entries underperform XX"
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


def x_apply_calendar_gates__mutmut_36(
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
                    "intraday management capability. 20yr backtest: friday entries underperform "
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


def x_apply_calendar_gates__mutmut_37(
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
                    "INTRADAY MANAGEMENT CAPABILITY. 20YR BACKTEST: FRIDAY ENTRIES UNDERPERFORM "
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


def x_apply_calendar_gates__mutmut_38(
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
                    "XXMon–Thu by ~0.40% avg return due to gap-open risk. XX"
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


def x_apply_calendar_gates__mutmut_39(
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
                    "mon–thu by ~0.40% avg return due to gap-open risk. "
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


def x_apply_calendar_gates__mutmut_40(
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
                    "MON–THU BY ~0.40% AVG RETURN DUE TO GAP-OPEN RISK. "
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


def x_apply_calendar_gates__mutmut_41(
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
                    "XXSignals with score≥65 (strong alt-data confirmation) are exempt.XX"
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


def x_apply_calendar_gates__mutmut_42(
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
                    "signals with score≥65 (strong alt-data confirmation) are exempt."
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


def x_apply_calendar_gates__mutmut_43(
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
                    "SIGNALS WITH SCORE≥65 (STRONG ALT-DATA CONFIRMATION) ARE EXEMPT."
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


def x_apply_calendar_gates__mutmut_44(
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
                "XXsentimentXX": "neg",
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


def x_apply_calendar_gates__mutmut_45(
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
                "SENTIMENT": "neg",
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


def x_apply_calendar_gates__mutmut_46(
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
                "sentiment": "XXnegXX",
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


def x_apply_calendar_gates__mutmut_47(
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
                "sentiment": "NEG",
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


def x_apply_calendar_gates__mutmut_48(
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
                "XXmetaXX": f"weekday=Friday(4) score={score:.1f}<65 | dow_gate=True",
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


def x_apply_calendar_gates__mutmut_49(
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
                "META": f"weekday=Friday(4) score={score:.1f}<65 | dow_gate=True",
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


def x_apply_calendar_gates__mutmut_50(
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
    _wk52l = None
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


def x_apply_calendar_gates__mutmut_51(
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
    _wk52l = info.get(None)
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


def x_apply_calendar_gates__mutmut_52(
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
    _wk52l = info.get("XXweek_52_lowXX")
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


def x_apply_calendar_gates__mutmut_53(
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
    _wk52l = info.get("WEEK_52_LOW")
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


def x_apply_calendar_gates__mutmut_54(
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
    if action == "BUY" and _wk52l and price or price > 0:
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


def x_apply_calendar_gates__mutmut_55(
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
    if action == "BUY" and _wk52l or price and price > 0:
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


def x_apply_calendar_gates__mutmut_56(
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
    if action == "BUY" or _wk52l and price and price > 0:
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


def x_apply_calendar_gates__mutmut_57(
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
    if action != "BUY" and _wk52l and price and price > 0:
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


def x_apply_calendar_gates__mutmut_58(
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
    if action == "XXBUYXX" and _wk52l and price and price > 0:
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


def x_apply_calendar_gates__mutmut_59(
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
    if action == "buy" and _wk52l and price and price > 0:
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


def x_apply_calendar_gates__mutmut_60(
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
    if action == "BUY" and _wk52l and price and price >= 0:
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


def x_apply_calendar_gates__mutmut_61(
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
    if action == "BUY" and _wk52l and price and price > 1:
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


def x_apply_calendar_gates__mutmut_62(
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
        _near_low = None
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


def x_apply_calendar_gates__mutmut_63(
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
        _near_low = (_wk52l > 0) or (price <= _wk52l * 1.08)
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


def x_apply_calendar_gates__mutmut_64(
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
        _near_low = (_wk52l >= 0) and (price <= _wk52l * 1.08)
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


def x_apply_calendar_gates__mutmut_65(
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
        _near_low = (_wk52l > 1) and (price <= _wk52l * 1.08)
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


def x_apply_calendar_gates__mutmut_66(
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
        _near_low = (_wk52l > 0) and (price < _wk52l * 1.08)
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


def x_apply_calendar_gates__mutmut_67(
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
        _near_low = (_wk52l > 0) and (price <= _wk52l / 1.08)
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


def x_apply_calendar_gates__mutmut_68(
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
        _near_low = (_wk52l > 0) and (price <= _wk52l * 2.08)
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


def x_apply_calendar_gates__mutmut_69(
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
            confidence = None
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


def x_apply_calendar_gates__mutmut_70(
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
            confidence = round(None, 1)
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


def x_apply_calendar_gates__mutmut_71(
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
            confidence = round(max(35.0, confidence - 4), None)
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


def x_apply_calendar_gates__mutmut_72(
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
            confidence = round(1)
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


def x_apply_calendar_gates__mutmut_73(
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
            confidence = round(max(35.0, confidence - 4), )
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


def x_apply_calendar_gates__mutmut_74(
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
            confidence = round(max(None, confidence - 4), 1)
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


def x_apply_calendar_gates__mutmut_75(
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
            confidence = round(max(35.0, None), 1)
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


def x_apply_calendar_gates__mutmut_76(
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
            confidence = round(max(confidence - 4), 1)
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


def x_apply_calendar_gates__mutmut_77(
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
            confidence = round(max(35.0, ), 1)
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


def x_apply_calendar_gates__mutmut_78(
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
            confidence = round(max(36.0, confidence - 4), 1)
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


def x_apply_calendar_gates__mutmut_79(
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
            confidence = round(max(35.0, confidence + 4), 1)
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


def x_apply_calendar_gates__mutmut_80(
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
            confidence = round(max(35.0, confidence - 5), 1)
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


def x_apply_calendar_gates__mutmut_81(
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
            confidence = round(max(35.0, confidence - 4), 2)
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


def x_apply_calendar_gates__mutmut_82(
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
            new_sources.add(None)
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


def x_apply_calendar_gates__mutmut_83(
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
            new_sources.add("XXRisk GateXX")
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


def x_apply_calendar_gates__mutmut_84(
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
            new_sources.add("risk gate")
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


def x_apply_calendar_gates__mutmut_85(
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
            new_sources.add("RISK GATE")
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


def x_apply_calendar_gates__mutmut_86(
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
                None
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_87(
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
                    "XXsrcXX": "Risk Gate",
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


def x_apply_calendar_gates__mutmut_88(
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
                    "SRC": "Risk Gate",
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


def x_apply_calendar_gates__mutmut_89(
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
                    "src": "XXRisk GateXX",
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


def x_apply_calendar_gates__mutmut_90(
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
                    "src": "risk gate",
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


def x_apply_calendar_gates__mutmut_91(
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
                    "src": "RISK GATE",
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


def x_apply_calendar_gates__mutmut_92(
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
                    "XXheadXX": "Near 52-Week Low — Structural Decline Risk −4pp (§77)",
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


def x_apply_calendar_gates__mutmut_93(
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
                    "HEAD": "Near 52-Week Low — Structural Decline Risk −4pp (§77)",
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


def x_apply_calendar_gates__mutmut_94(
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
                    "head": "XXNear 52-Week Low — Structural Decline Risk −4pp (§77)XX",
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


def x_apply_calendar_gates__mutmut_95(
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
                    "head": "near 52-week low — structural decline risk −4pp (§77)",
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


def x_apply_calendar_gates__mutmut_96(
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
                    "head": "NEAR 52-WEEK LOW — STRUCTURAL DECLINE RISK −4PP (§77)",
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


def x_apply_calendar_gates__mutmut_97(
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
                    "XXbodyXX": (
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


def x_apply_calendar_gates__mutmut_98(
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
                    "BODY": (
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


def x_apply_calendar_gates__mutmut_99(
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
                        "XXLive-data audit (546 trades): signals near 52-week lows win only XX"
                        "31% of the time (−11.5pp vs baseline). These stocks are in "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_100(
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
                        "live-data audit (546 trades): signals near 52-week lows win only "
                        "31% of the time (−11.5pp vs baseline). These stocks are in "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_101(
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
                        "LIVE-DATA AUDIT (546 TRADES): SIGNALS NEAR 52-WEEK LOWS WIN ONLY "
                        "31% of the time (−11.5pp vs baseline). These stocks are in "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_102(
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
                        "XX31% of the time (−11.5pp vs baseline). These stocks are in XX"
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_103(
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
                        "31% of the time (−11.5pp vs baseline). these stocks are in "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_104(
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
                        "31% OF THE TIME (−11.5PP VS BASELINE). THESE STOCKS ARE IN "
                        "structural decline — the dip is fundamental, not a recoverable "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_105(
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
                        "XXstructural decline — the dip is fundamental, not a recoverable XX"
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_106(
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
                        "STRUCTURAL DECLINE — THE DIP IS FUNDAMENTAL, NOT A RECOVERABLE "
                        "oversold. Confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_107(
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
                        "XXoversold. Confidence reduced −4pp.XX"
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_108(
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
                        "oversold. confidence reduced −4pp."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_109(
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
                        "OVERSOLD. CONFIDENCE REDUCED −4PP."
                    ),
                    "sentiment": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_110(
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
                    "XXsentimentXX": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_111(
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
                    "SENTIMENT": "neg",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_112(
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
                    "sentiment": "XXnegXX",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_113(
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
                    "sentiment": "NEG",
                    "meta": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_114(
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
                    "XXmetaXX": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_115(
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
                    "META": "near_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_116(
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
                    "meta": "XXnear_52wk_low=True penalty=-4pp §77 (inverted 2026-05-31)XX",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_117(
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
                    "meta": "near_52wk_low=true penalty=-4pp §77 (inverted 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources


def x_apply_calendar_gates__mutmut_118(
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
                    "meta": "NEAR_52WK_LOW=TRUE PENALTY=-4PP §77 (INVERTED 2026-05-31)",
                }
            )

    return action, confidence, cards, new_sources

mutants_x_apply_calendar_gates__mutmut['_mutmut_orig'] = x_apply_calendar_gates__mutmut_orig # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_1'] = x_apply_calendar_gates__mutmut_1 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_2'] = x_apply_calendar_gates__mutmut_2 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_3'] = x_apply_calendar_gates__mutmut_3 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_4'] = x_apply_calendar_gates__mutmut_4 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_5'] = x_apply_calendar_gates__mutmut_5 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_6'] = x_apply_calendar_gates__mutmut_6 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_7'] = x_apply_calendar_gates__mutmut_7 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_8'] = x_apply_calendar_gates__mutmut_8 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_9'] = x_apply_calendar_gates__mutmut_9 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_10'] = x_apply_calendar_gates__mutmut_10 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_11'] = x_apply_calendar_gates__mutmut_11 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_12'] = x_apply_calendar_gates__mutmut_12 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_13'] = x_apply_calendar_gates__mutmut_13 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_14'] = x_apply_calendar_gates__mutmut_14 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_15'] = x_apply_calendar_gates__mutmut_15 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_16'] = x_apply_calendar_gates__mutmut_16 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_17'] = x_apply_calendar_gates__mutmut_17 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_18'] = x_apply_calendar_gates__mutmut_18 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_19'] = x_apply_calendar_gates__mutmut_19 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_20'] = x_apply_calendar_gates__mutmut_20 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_21'] = x_apply_calendar_gates__mutmut_21 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_22'] = x_apply_calendar_gates__mutmut_22 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_23'] = x_apply_calendar_gates__mutmut_23 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_24'] = x_apply_calendar_gates__mutmut_24 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_25'] = x_apply_calendar_gates__mutmut_25 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_26'] = x_apply_calendar_gates__mutmut_26 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_27'] = x_apply_calendar_gates__mutmut_27 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_28'] = x_apply_calendar_gates__mutmut_28 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_29'] = x_apply_calendar_gates__mutmut_29 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_30'] = x_apply_calendar_gates__mutmut_30 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_31'] = x_apply_calendar_gates__mutmut_31 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_32'] = x_apply_calendar_gates__mutmut_32 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_33'] = x_apply_calendar_gates__mutmut_33 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_34'] = x_apply_calendar_gates__mutmut_34 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_35'] = x_apply_calendar_gates__mutmut_35 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_36'] = x_apply_calendar_gates__mutmut_36 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_37'] = x_apply_calendar_gates__mutmut_37 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_38'] = x_apply_calendar_gates__mutmut_38 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_39'] = x_apply_calendar_gates__mutmut_39 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_40'] = x_apply_calendar_gates__mutmut_40 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_41'] = x_apply_calendar_gates__mutmut_41 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_42'] = x_apply_calendar_gates__mutmut_42 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_43'] = x_apply_calendar_gates__mutmut_43 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_44'] = x_apply_calendar_gates__mutmut_44 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_45'] = x_apply_calendar_gates__mutmut_45 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_46'] = x_apply_calendar_gates__mutmut_46 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_47'] = x_apply_calendar_gates__mutmut_47 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_48'] = x_apply_calendar_gates__mutmut_48 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_49'] = x_apply_calendar_gates__mutmut_49 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_50'] = x_apply_calendar_gates__mutmut_50 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_51'] = x_apply_calendar_gates__mutmut_51 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_52'] = x_apply_calendar_gates__mutmut_52 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_53'] = x_apply_calendar_gates__mutmut_53 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_54'] = x_apply_calendar_gates__mutmut_54 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_55'] = x_apply_calendar_gates__mutmut_55 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_56'] = x_apply_calendar_gates__mutmut_56 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_57'] = x_apply_calendar_gates__mutmut_57 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_58'] = x_apply_calendar_gates__mutmut_58 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_59'] = x_apply_calendar_gates__mutmut_59 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_60'] = x_apply_calendar_gates__mutmut_60 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_61'] = x_apply_calendar_gates__mutmut_61 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_62'] = x_apply_calendar_gates__mutmut_62 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_63'] = x_apply_calendar_gates__mutmut_63 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_64'] = x_apply_calendar_gates__mutmut_64 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_65'] = x_apply_calendar_gates__mutmut_65 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_66'] = x_apply_calendar_gates__mutmut_66 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_67'] = x_apply_calendar_gates__mutmut_67 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_68'] = x_apply_calendar_gates__mutmut_68 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_69'] = x_apply_calendar_gates__mutmut_69 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_70'] = x_apply_calendar_gates__mutmut_70 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_71'] = x_apply_calendar_gates__mutmut_71 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_72'] = x_apply_calendar_gates__mutmut_72 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_73'] = x_apply_calendar_gates__mutmut_73 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_74'] = x_apply_calendar_gates__mutmut_74 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_75'] = x_apply_calendar_gates__mutmut_75 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_76'] = x_apply_calendar_gates__mutmut_76 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_77'] = x_apply_calendar_gates__mutmut_77 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_78'] = x_apply_calendar_gates__mutmut_78 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_79'] = x_apply_calendar_gates__mutmut_79 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_80'] = x_apply_calendar_gates__mutmut_80 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_81'] = x_apply_calendar_gates__mutmut_81 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_82'] = x_apply_calendar_gates__mutmut_82 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_83'] = x_apply_calendar_gates__mutmut_83 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_84'] = x_apply_calendar_gates__mutmut_84 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_85'] = x_apply_calendar_gates__mutmut_85 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_86'] = x_apply_calendar_gates__mutmut_86 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_87'] = x_apply_calendar_gates__mutmut_87 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_88'] = x_apply_calendar_gates__mutmut_88 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_89'] = x_apply_calendar_gates__mutmut_89 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_90'] = x_apply_calendar_gates__mutmut_90 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_91'] = x_apply_calendar_gates__mutmut_91 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_92'] = x_apply_calendar_gates__mutmut_92 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_93'] = x_apply_calendar_gates__mutmut_93 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_94'] = x_apply_calendar_gates__mutmut_94 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_95'] = x_apply_calendar_gates__mutmut_95 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_96'] = x_apply_calendar_gates__mutmut_96 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_97'] = x_apply_calendar_gates__mutmut_97 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_98'] = x_apply_calendar_gates__mutmut_98 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_99'] = x_apply_calendar_gates__mutmut_99 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_100'] = x_apply_calendar_gates__mutmut_100 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_101'] = x_apply_calendar_gates__mutmut_101 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_102'] = x_apply_calendar_gates__mutmut_102 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_103'] = x_apply_calendar_gates__mutmut_103 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_104'] = x_apply_calendar_gates__mutmut_104 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_105'] = x_apply_calendar_gates__mutmut_105 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_106'] = x_apply_calendar_gates__mutmut_106 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_107'] = x_apply_calendar_gates__mutmut_107 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_108'] = x_apply_calendar_gates__mutmut_108 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_109'] = x_apply_calendar_gates__mutmut_109 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_110'] = x_apply_calendar_gates__mutmut_110 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_111'] = x_apply_calendar_gates__mutmut_111 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_112'] = x_apply_calendar_gates__mutmut_112 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_113'] = x_apply_calendar_gates__mutmut_113 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_114'] = x_apply_calendar_gates__mutmut_114 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_115'] = x_apply_calendar_gates__mutmut_115 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_116'] = x_apply_calendar_gates__mutmut_116 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_117'] = x_apply_calendar_gates__mutmut_117 # type: ignore # mutmut generated
mutants_x_apply_calendar_gates__mutmut['x_apply_calendar_gates__mutmut_118'] = x_apply_calendar_gates__mutmut_118 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCalendarGateǁ__repr____mutmut: MutantDict = {}  # type: ignore


# ── GateBase class (Strategy Pattern API) ─────────────────────────────────────


class CalendarGate:
    """
    GateBase wrapper around apply_calendar_gates().
    Use in a GatePipeline; the functional API above is kept for direct calls.
    """

    @_mutmut_mutated(mutants_xǁCalendarGateǁapply__mutmut)
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

    def xǁCalendarGateǁapply__mutmut_orig(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
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

    def xǁCalendarGateǁapply__mutmut_1(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = None
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_2(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=None,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_3(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=None,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_4(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=None,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_5(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=None,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_6(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=None,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_7(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=None,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_8(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=None,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_9(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_10(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_11(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_12(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_13(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_14(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            info=ctx.info,
        )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_15(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            )
        ctx.rationale.extend(_cards)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_16(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
        ctx.action, ctx.confidence, _cards, _srcs = apply_calendar_gates(
            action=ctx.action,
            confidence=ctx.confidence,
            score=ctx.score,
            today_dow=ctx.today_dow,
            month=ctx.month,
            price=ctx.price,
            info=ctx.info,
        )
        ctx.rationale.extend(None)
        ctx.sources.update(_srcs)

    def xǁCalendarGateǁapply__mutmut_17(self, ctx: SignalContext) -> None:  # type: ignore[name-defined]
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
        ctx.sources.update(None)

    @_mutmut_mutated(mutants_xǁCalendarGateǁ__repr____mutmut)
    def __repr__(self) -> str:
        return "CalendarGate"

    def xǁCalendarGateǁ__repr____mutmut_orig(self) -> str:
        return "CalendarGate"

    def xǁCalendarGateǁ__repr____mutmut_1(self) -> str:
        return "XXCalendarGateXX"

    def xǁCalendarGateǁ__repr____mutmut_2(self) -> str:
        return "calendargate"

    def xǁCalendarGateǁ__repr____mutmut_3(self) -> str:
        return "CALENDARGATE"

mutants_xǁCalendarGateǁapply__mutmut['_mutmut_orig'] = CalendarGate.xǁCalendarGateǁapply__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_1'] = CalendarGate.xǁCalendarGateǁapply__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_2'] = CalendarGate.xǁCalendarGateǁapply__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_3'] = CalendarGate.xǁCalendarGateǁapply__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_4'] = CalendarGate.xǁCalendarGateǁapply__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_5'] = CalendarGate.xǁCalendarGateǁapply__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_6'] = CalendarGate.xǁCalendarGateǁapply__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_7'] = CalendarGate.xǁCalendarGateǁapply__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_8'] = CalendarGate.xǁCalendarGateǁapply__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_9'] = CalendarGate.xǁCalendarGateǁapply__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_10'] = CalendarGate.xǁCalendarGateǁapply__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_11'] = CalendarGate.xǁCalendarGateǁapply__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_12'] = CalendarGate.xǁCalendarGateǁapply__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_13'] = CalendarGate.xǁCalendarGateǁapply__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_14'] = CalendarGate.xǁCalendarGateǁapply__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_15'] = CalendarGate.xǁCalendarGateǁapply__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_16'] = CalendarGate.xǁCalendarGateǁapply__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁapply__mutmut['xǁCalendarGateǁapply__mutmut_17'] = CalendarGate.xǁCalendarGateǁapply__mutmut_17 # type: ignore # mutmut generated

mutants_xǁCalendarGateǁ__repr____mutmut['_mutmut_orig'] = CalendarGate.xǁCalendarGateǁ__repr____mutmut_orig # type: ignore # mutmut generated
mutants_xǁCalendarGateǁ__repr____mutmut['xǁCalendarGateǁ__repr____mutmut_1'] = CalendarGate.xǁCalendarGateǁ__repr____mutmut_1 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁ__repr____mutmut['xǁCalendarGateǁ__repr____mutmut_2'] = CalendarGate.xǁCalendarGateǁ__repr____mutmut_2 # type: ignore # mutmut generated
mutants_xǁCalendarGateǁ__repr____mutmut['xǁCalendarGateǁ__repr____mutmut_3'] = CalendarGate.xǁCalendarGateǁ__repr____mutmut_3 # type: ignore # mutmut generated
